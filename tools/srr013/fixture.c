#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Zero-filled image pages place the synthetic publications at the SRR-012 RVAs. */
#pragma bss_seg(push, fixture_image, ".srr")
static volatile unsigned char image_tail[0x82f0000];
#pragma bss_seg(pop, fixture_image)
static unsigned char *image;
static unsigned char *index_header;
static const uint16_t discriminator = 37;

typedef struct { uint64_t first, second; } Key;
typedef struct {
    uint32_t owner, seed, biome, override_id, biome_rsgd;
    uint32_t slots[7];
} Sample;

/* Direct transcription of the fixed public sample table, independent of the reader. */
static const Sample samples[] = {
    {0x0003f59f, 2842708811u, 0x000d9bac, 0, 0x000083f0,
     {0x57ea, 0, 0, 0x57e9, 0, 0, 0x83ec}},
    {0x0003f59f, 2842708811u, 0x0023c0ce, 0x00244ccb, 0x00007edd,
     {0x57c7, 0x57c9, 0, 0, 0, 0, 0}},
    {0x0003f59f, 2842708811u, 0x002c9985, 0x00244ccc, 0x000083ea,
     {0x57c1, 0x57c3, 0, 0, 0, 0, 0}},
    {0x0005df7f, 1633829920u, 0x000c5717, 0x0018ce00, 0x000083e0,
     {0x57eb, 0x57ec, 0, 0, 0x5df8, 0x57f5, 0}},
};

typedef struct { uint32_t id; unsigned char *form; } Form;
typedef struct {
    Key key;
    const Sample *sample;
    uint16_t size;
} Row;
typedef struct {
    unsigned char *address;
    Key first;
} Node;
typedef struct {
    Node root;
    uint64_t count;
    unsigned char *edges[4];
} Tree;

static Form forms[32];
static size_t form_count;
static Tree primary, inserted, removed;
static volatile LONG stop_race;
static const char *mode;

static void require(int condition, const char *reason)
{
    if (!condition) {
        fprintf(stderr, "fixture: %s\n", reason);
        exit(2);
    }
}

static int is_mode(const char *name) { return strcmp(mode, name) == 0; }
static void put16(unsigned char *p, uint16_t value) { memcpy(p, &value, 2); }
static void put32(unsigned char *p, uint32_t value) { memcpy(p, &value, 4); }
static void put64(unsigned char *p, uint64_t value) { memcpy(p, &value, 8); }
static void putptr(unsigned char *p, const void *value) { put64(p, (uintptr_t)value); }

static uint32_t get32(const unsigned char *p)
{
    uint32_t value;
    memcpy(&value, p, 4);
    return value;
}

static void putkey(unsigned char *p, Key key)
{
    put64(p, key.first);
    put64(p + 8, key.second);
}

static unsigned char *make_page(void)
{
    unsigned char *page = VirtualAlloc(NULL, 4096, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    require(page != NULL, "VirtualAlloc failed");
    return page;
}

static unsigned char *record(uint32_t id, unsigned char type)
{
    for (size_t i = 0; i < form_count; ++i)
        if (forms[i].id == id) return forms[i].form;
    require(form_count < _countof(forms), "form fixture overflow");
    unsigned char *form = make_page();
    put32(form + 0x28, id);
    form[0x2e] = type;
    forms[form_count++] = (Form){id, form};
    return form;
}

static uint32_t hash_slot(uint32_t id, uint32_t capacity)
{
    uint64_t hash = UINT64_C(0xcbf29ce484222325);
    for (unsigned i = 0; i < 4; ++i) {
        hash ^= (id >> (8 * i)) & 0xff;
        hash *= UINT64_C(0x100000001b3);
    }
    return (uint32_t)(hash & (capacity - 1));
}

static void make_forms(void)
{
    for (size_t i = 0; i < _countof(samples); ++i) {
        const Sample *sample = &samples[i];
        unsigned char *pndt = record(sample->owner, 0xba);
        unsigned char *biom = record(sample->biome, 0xa0);
        unsigned char *rnam = record(sample->biome_rsgd, 0xab);
        put32(pndt + 0x50, sample->seed);
        put32(pndt + 0x54, sample->owner);
        put32(biom + 0x308, 1);
        putptr(biom + 0x310, biom + 0x400);
        putptr(biom + 0x400, rnam);
        if (sample->override_id) (void)record(sample->override_id, 0xab);
    }
    if (is_mode("wrong-rnam")) {
        unsigned char *mountains = record(samples[1].biome, 0xa0);
        putptr(mountains + 0x400, record(samples[0].biome_rsgd, 0xab));
    }
    if (is_mode("wrong-seed")) put32(record(samples[0].owner, 0xba) + 0x50, 0);

    /* Reserve every home slot before placing overflow entries in the same table. */
    enum { CAPACITY = 32, STRIDE = 0x18 };
    uint32_t homes[CAPACITY] = {0};
    unsigned char *table = make_page();
    for (uint32_t i = 0; i < CAPACITY; ++i) put32(table + i * STRIDE + 0x10, UINT32_MAX);
    for (size_t i = 0; i < form_count; ++i) homes[hash_slot(forms[i].id, CAPACITY)] = 1;
    unsigned collisions = 0;
    unsigned char *mountains_entry = NULL;
    for (size_t i = 0; i < form_count; ++i) {
        const uint32_t id = forms[i].id;
        uint32_t slot = hash_slot(id, CAPACITY);
        unsigned char *entry = table + slot * STRIDE;
        if (get32(entry + 0x10) != UINT32_MAX) {
            while (get32(entry + 0x10) != CAPACITY)
                entry = table + get32(entry + 0x10) * STRIDE;
            for (slot = 0; slot < CAPACITY; ++slot)
                if (!homes[slot] && get32(table + slot * STRIDE + 0x10) == UINT32_MAX) break;
            require(slot < CAPACITY, "form map has no overflow slot");
            put32(entry + 0x10, slot);
            entry = table + slot * STRIDE;
            ++collisions;
        }
        put32(entry, id);
        unsigned char *form = forms[i].form;
        if (is_mode("wrong-map") && id == samples[1].biome) form = record(samples[0].biome, 0xa0);
        if (id == samples[1].biome) mountains_entry = entry;
        putptr(entry + 8, form);
        put32(entry + 0x10, CAPACITY);
    }
    require(collisions != 0, "form map collision coverage missing");
    if (is_mode("map-loop")) {
        require(mountains_entry != NULL, "Mountains form entry missing");
        put32(mountains_entry, 0xeeeeeeee);
        put32(mountains_entry + 0x10, (uint32_t)((mountains_entry - table) / STRIDE));
    }
    unsigned char *map = make_page();
    putptr(map + 0x10, table);
    put64(map + 0x18, CAPACITY);
    putptr(image + 0x5e60ea0, map);
}

static uint64_t owner_key(uint32_t owner)
{
    return ((uint64_t)owner << 32) | UINT64_C(0x10000) | discriminator;
}

static Row sample_row(size_t i)
{
    return (Row){{owner_key(samples[i].owner), samples[i].biome}, &samples[i], 0x90};
}

static Node block(const Row *rows, unsigned count, Tree *tree, int faults)
{
    unsigned char *data = make_page();
    unsigned position = 0xfe0;
    put32(data, UINT32_MAX);
    put32(data + 4, count);
    put32(data + 8, 0x10 + 4 * count);
    for (unsigned i = 0; i < count; ++i) {
        const Row *row = &rows[i];
        require(position >= row->size + 0x10u + 4u * count, "packed fixture overflow");
        position -= row->size;
        put16(data + 0x10 + 4 * i, row->size);
        put16(data + 0x12 + 4 * i, (uint16_t)position);
        unsigned char *edge = data + position;
        putkey(edge + 0x10, row->key);
        putptr(edge, image + 0x4b3d260);
        if (row->sample) {
            const Sample *sample = row->sample;
            size_t sample_index = (size_t)(sample - samples);
            putptr(edge, image + 0x4b3d258);
            put32(edge + 0x60, sample->biome);
            put32(edge + 0x6c, sample->override_id);
            int zero = faults && (is_mode("zero") ||
                                   ((is_mode("mixed") || is_mode("ineligible-zero")) && sample_index == 1));
            if (!zero)
                memcpy(edge + 0x70, sample->slots, sizeof(sample->slots));
            if (faults && sample_index == 1 && is_mode("wrong-type")) putptr(edge, image + 0x4b3d260);
            if (faults && sample_index == 1 && (is_mode("wrong-override") || is_mode("ineligible-zero")))
                put32(edge + 0x6c, 0);
            if (faults && sample_index == 1 && is_mode("wrong-biom")) put32(edge + 0x60, samples[0].biome);
            if (faults && sample_index == 2 && is_mode("mixed")) put32(edge + 0x70, 0x57eb);
            if (tree->edges[sample_index] == NULL) tree->edges[sample_index] = edge;
        }
    }
    put32(data + 0xC, position);
    tree->count += count;
    return (Node){data, rows[0].key};
}

static Node leaf(const Node *blocks, unsigned count)
{
    unsigned char *data = make_page();
    put32(data + 4, count);
    for (unsigned i = 0; i < count; ++i) {
        putkey(data + 0x18 + 0x10 * i, blocks[i].first);
        putptr(data + 0xa98 + 8 * i, blocks[i].address);
    }
    return (Node){data, blocks[0].first};
}

static Node internal(const Node *children, unsigned count, uint32_t level)
{
    unsigned char *data = make_page();
    put32(data, level);
    put32(data + 4, count - 1);
    for (unsigned i = 0; i < count; ++i) {
        if (i) putkey(data + 8 + 0x10 * (i - 1), children[i].first);
        putptr(data + 0xa88 + 8 * i, children[i].address);
    }
    return (Node){data, children[0].first};
}

static void link_leaves(Node *leaves, unsigned count)
{
    for (unsigned i = 0; i < count; ++i) {
        if (i) putptr(leaves[i].address + 0x10, leaves[i - 1].address);
        if (i + 1 < count) putptr(leaves[i].address + 8, leaves[i + 1].address);
    }
}

/* variant -1 removes Mountains; variant +1 inserts an extra boundary record. */
static void make_tree(Tree *tree, int depth, int variant, int faults)
{
    const uint64_t kreet = owner_key(samples[0].owner);
    const uint64_t decaran = owner_key(samples[3].owner);
    Row first[3] = {{{kreet - 1, 3}, NULL, 0x28}, sample_row(0)};
    Row second[2] = {sample_row(1)};
    Row third[4] = {
        sample_row(2),
        {{kreet, UINT64_C(0x8000ffffffffffff)}, NULL, 0x28},
        {{decaran - 1, 0}, NULL, 0x30},
    };
    Row fourth[] = {sample_row(3), {{decaran + 1, 0}, NULL, 0x20}};
    unsigned second_count = 1;
    unsigned third_count = 3;
    unsigned fourth_count = faults && is_mode("root-end") ? 1 : (unsigned)_countof(fourth);
    if (variant < 0 || (faults && (is_mode("absent") || is_mode("wrong-owner")))) {
        second_count = 0;
    }
    if (faults && is_mode("wrong-owner")) {
        first[2] = first[1];
        first[1] = sample_row(1);
        first[1].key.first = kreet - 1;
    }
    if (faults && is_mode("leaf-decoy")) {
        second[1] = second[0];
        second[0] = sample_row(0);
        second_count = 2;
    }
    if (faults && is_mode("duplicate")) {
        third[3] = third[2];
        third[2] = third[1];
        third[1] = third[0];
        third_count = 4;
    }
    const unsigned first_count = faults && is_mode("wrong-owner") ? 3 : 2;
    if (depth < 0) {
        Row all[12];
        unsigned n = 0;
        for (unsigned i = 0; i < first_count; ++i) all[n++] = first[i];
        for (unsigned i = 0; i < second_count; ++i) all[n++] = second[i];
        for (unsigned i = 0; i < third_count; ++i) all[n++] = third[i];
        for (unsigned i = 0; i < fourth_count; ++i) all[n++] = fourth[i];
        tree->root = block(all, n, tree, faults);
        return;
    }
    Node blocks[6];
    unsigned block_count = 0;
    blocks[block_count++] = block(first, first_count - 1, tree, faults);
    blocks[block_count++] = block(first + first_count - 1, 1, tree, faults);
    if (second_count) blocks[block_count++] = block(second, second_count, tree, faults);
    if (faults && is_mode("holes")) {
        const Row deleted = {{kreet + 1, 0}, NULL, 0x28};
        const Row with_hole[] = {third[0], third[1], deleted, third[2]};
        Node packed = block(with_hole, (unsigned)_countof(with_hole), tree, faults);
        /* Removing a directory entry leaves its bytes between occupied spans. */
        put32(packed.address + 0x18, get32(packed.address + 0x1c));
        put32(packed.address + 4, 3);
        put16(packed.address + 8, 0x1c);
        put16(packed.address + 0xa, deleted.size);
        --tree->count;
        blocks[block_count++] = packed;
    } else {
        blocks[block_count++] = block(third, third_count, tree, faults);
    }
    if (variant > 0) {
        const Row extra = {{decaran + 1, 0}, NULL, 0x20};
        /* Insert before the previous terminal row so the range's fence changes. */
        Row end[] = {fourth[0], extra, fourth[1]};
        end[2].key.second = 1;
        blocks[block_count++] = block(end, (unsigned)_countof(end), tree, faults);
    } else {
        blocks[block_count++] = block(fourth, fourth_count, tree, faults);
    }
    if (depth == 0) {
        if (faults && is_mode("lying-minimum")) {
            /* An apparently sorted trailing block hides a second Frozen edge. */
            Row hidden = sample_row(0);
            blocks[block_count] = block(&hidden, 1, tree, faults);
            blocks[block_count++].first = (Key){decaran + 2, 0};
        }
        tree->root = leaf(blocks, block_count);
        return;
    }
    Node leaves[5];
    unsigned leaf_count = 0;
    if (faults && is_mode("predecessor")) {
        leaves[leaf_count++] = leaf(blocks, 1);
        leaves[leaf_count++] = leaf(blocks + 1, 1);
    } else {
        leaves[leaf_count++] = leaf(blocks, 2);
    }
    for (unsigned i = 2; i < block_count; ++i) leaves[leaf_count++] = leaf(blocks + i, 1);
    link_leaves(leaves, leaf_count);
    if (depth == 2) {
        const Node children[] = {internal(leaves, 2, 1), internal(leaves + 2, leaf_count - 2, 1)};
        tree->root = internal(children, (unsigned)_countof(children), 2);
    } else {
        tree->root = internal(leaves, leaf_count, 1);
    }
    if (faults && is_mode("predecessor")) putkey(tree->root.address + 8, (Key){kreet - 1, 4});
    if (faults && is_mode("loop")) putptr(leaves[1].address + 8, leaves[1].address);
    if (faults && is_mode("bad-count")) put32(tree->root.address + 4, 0xa9);
    if (faults && is_mode("bad-minimum")) putkey(leaves[1].address + 0x18, (Key){kreet, 0});
    if (faults && is_mode("bad-directory")) put32(blocks[2].address + 8, 0x10);
    if (faults && is_mode("overlap")) {
        put32(blocks[3].address + 0x14, get32(blocks[3].address + 0x10));
    }
    if (faults && is_mode("unaligned")) putptr(tree->root.address + 0xa88, leaves[0].address + 1);
    if (faults && is_mode("unreadable")) {
        DWORD previous;
        require(VirtualProtect(blocks[2].address, 4096, PAGE_NOACCESS, &previous), "VirtualProtect failed");
    }
}

static void make_excessive(Tree *tree)
{
    enum { LEAVES = 130 };
    Node leaves[LEAVES];
    const uint64_t owner = owner_key(samples[0].owner);
    for (unsigned i = 0; i < LEAVES; ++i) {
        const Row row = {{owner, 1u + i}, NULL, 0x90};
        const Node packed = block(&row, 1, tree, 0);
        /* These other BIOM keys are structurally valid and within the requested range. */
        unsigned char *edge = packed.address + 0xfe0 - 0x90;
        putptr(edge, image + 0x4b3d258);
        put32(edge + 0x60, (uint32_t)row.key.second);
        leaves[i] = leaf(&packed, 1);
    }
    link_leaves(leaves, LEAVES);
    tree->root = internal(leaves, LEAVES, 1);
}

static void publish_tree(const Tree *tree)
{
    putptr(index_header, tree->root.address);
    put64(index_header + 0x48, tree->count);
}

static void slots(const Tree *tree, int restore)
{
    const uint32_t cleared[7] = {0};
    for (size_t i = 0; i < _countof(samples); ++i)
        if (tree->edges[i]) memcpy(tree->edges[i] + 0x70, restore ? samples[i].slots : cleared, sizeof(cleared));
}

static DWORD WINAPI race(LPVOID unused)
{
    (void)unused;
    while (InterlockedCompareExchange(&stop_race, 0, 0) == 0) {
        slots(&primary, 0);
        publish_tree(&inserted);
        Sleep(1);
        publish_tree(&removed);
        Sleep(1);
        publish_tree(&primary);
        slots(&primary, 1);
        Sleep(1);
    }
    return 0;
}

static void end_race(HANDLE *worker)
{
    if (!*worker) return;
    InterlockedExchange(&stop_race, 1);
    require(WaitForSingleObject(*worker, 2000) == WAIT_OBJECT_0, "writer thread did not stop");
    CloseHandle(*worker);
    *worker = NULL;
    publish_tree(&primary);
    slots(&primary, 1);
}

static void build_target(void)
{
    image = (unsigned char *)GetModuleHandleW(NULL);
    image_tail[0] = 1;
    image_tail[sizeof(image_tail) - 1] = 1;
    require((uintptr_t)image_tail < (uintptr_t)(image + 0x4b3d258) &&
            (uintptr_t)(image + 0x82eec30) < (uintptr_t)(image_tail + sizeof(image_tail)),
            "zero-fill image does not cover SRR-012 RVAs");

    unsigned char *context = image + 0x82ee5c0;
    index_header = context + 0x300;
    unsigned char *receiver = make_page();
    unsigned char *registry = make_page();
    putptr(context, image + 0x4d6a6c0);
    putptr(receiver, image + 0x4d5fac8);
    putptr(image + 0x61fa160, receiver);
    put16(image + 0x61dfa4c, is_mode("unregistered") ? UINT16_MAX : discriminator);
    put32(image + 0x82eec20, 64);
    putptr(image + 0x82eec28, registry);
    putptr(registry + 0x18 * discriminator, receiver + (is_mode("wrong-registry") ? 0x108 : 0x100));
    make_forms();

    if (is_mode("excessive")) make_excessive(&primary);
    else if (!is_mode("empty")) {
        int depth = 1;
        if (is_mode("direct")) depth = -1;
        if (is_mode("leaf-only") || is_mode("lying-minimum")) depth = 0;
        if (is_mode("depth2")) depth = 2;
        make_tree(&primary, depth, 0, 1);
    }
    make_tree(&inserted, 1, 1, 0);
    make_tree(&removed, 1, -1, 0);
    publish_tree(&primary);
    if (!is_mode("context-absent")) {
        if (is_mode("context-decoy")) {
            unsigned char *decoy = make_page();
            memcpy(decoy, context, 0x350);
            context = decoy;
        }
        putptr(image + 0x82eebb0, context);
    }
    if (is_mode("wrong-context-vptr")) putptr(context, image + 0x4d6a6c8);
    if (is_mode("mapped-image")) {
        /* Change only this fixture's non-code mapped PE timestamp; retain the disk file. */
        DWORD protection, unused;
        unsigned char *timestamp = image + get32(image + 0x3c) + 8;
        require(VirtualProtect(timestamp, 4, PAGE_READWRITE, &protection), "header protection change failed");
        put32(timestamp, get32(timestamp) ^ 1u);
        require(VirtualProtect(timestamp, 4, protection, &unused), "header protection restore failed");
    }
    if (is_mode("no-read-rights")) {
        SECURITY_DESCRIPTOR security;
        ACL empty_acl;
        require(InitializeSecurityDescriptor(&security, SECURITY_DESCRIPTOR_REVISION) &&
                InitializeAcl(&empty_acl, sizeof(empty_acl), ACL_REVISION) &&
                SetSecurityDescriptorDacl(&security, TRUE, &empty_acl, FALSE) &&
                SetKernelObjectSecurity(GetCurrentProcess(), DACL_SECURITY_INFORMATION, &security),
                "owned fixture could not set its deny-all DACL");
    }
}

int main(int argc, char **argv)
{
    static const char *const modes[] = {
        "populated", "zero", "mixed", "direct", "leaf-only", "depth2", "holes", "root-end", "absent", "duplicate",
        "wrong-owner", "wrong-type", "wrong-registry", "wrong-map", "map-loop", "wrong-rnam", "wrong-seed",
        "wrong-override", "ineligible-zero", "wrong-biom", "unaligned", "unreadable", "loop", "bad-count", "overlap",
        "bad-directory", "bad-minimum", "excessive", "leaf-decoy", "empty", "mapped-image",
        "no-read-rights", "context-absent", "context-decoy", "wrong-context-vptr", "unregistered", "predecessor",
        "lying-minimum",
    };
    require(argc == 2, "provide one fixture scenario");
    mode = argv[1];
    size_t i = 0;
    while (i < _countof(modes) && !is_mode(modes[i])) ++i;
    require(i != _countof(modes), "unknown scenario");
    build_target();
    setvbuf(stdout, NULL, _IONBF, 0);
    puts("READY");
    char command[32];
    HANDLE worker = NULL;
    while (fgets(command, sizeof(command), stdin)) {
        command[strcspn(command, "\r\n")] = '\0';
        if (!strcmp(command, "quit")) break;
        if (!strcmp(command, "stop")) end_race(&worker);
        else {
            require(worker == NULL, "writer already active");
            if (!strcmp(command, "clear")) slots(&primary, 0);
            else if (!strcmp(command, "restore")) slots(&primary, 1);
            else if (!strcmp(command, "insert")) publish_tree(&inserted);
            else if (!strcmp(command, "remove")) publish_tree(&removed);
            else if (!strcmp(command, "restore-tree")) publish_tree(&primary);
            else if (!strcmp(command, "aba")) {
                slots(&primary, 0);
                publish_tree(&inserted);
                Sleep(1);
                publish_tree(&primary);
                slots(&primary, 1);
            } else if (!strcmp(command, "race")) {
                InterlockedExchange(&stop_race, 0);
                worker = CreateThread(NULL, 0, race, NULL, 0, NULL);
                require(worker != NULL, "owned writer thread creation failed");
            } else {
                require(0, "unknown command");
            }
        }
        puts("ACK");
    }
    end_race(&worker);
    return 0;
}
