#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Synthesize the fixed retail RVAs without file-backed game bytes. */
#pragma bss_seg(push, fixture_image, ".srr")
static volatile unsigned char image_tail[0x82f0000];
#pragma bss_seg(pop, fixture_image)

#ifndef SRR_FIXTURE_MAP_CAPACITY
#define SRR_FIXTURE_MAP_CAPACITY 16384
#endif

enum {
    BLOCK_END = 0xfe0, MAP_CAP = SRR_FIXTURE_MAP_CAPACITY, DISC = 37, BIOM = 0x200000,
    OWNER = 0x100000, EXCEPTIONAL_OWNER = 0x1fffe0, RSGD = 0x300000, RESOURCE = 0x400000,
};

typedef unsigned char Byte;
typedef struct { uint64_t high, low; } Key;
typedef struct { Key key; unsigned width; uint32_t slots[7]; } Row;
typedef struct { Byte *page; Key minimum; } Node;
typedef struct {
    Node root;
    size_t count;
    size_t windows;
    size_t blocks;
    size_t leaves;
    size_t depth;
    Byte **edges;
    Byte *first_block;
    Byte *first_leaf;
    Byte *first_branch;
} Tree;
typedef struct { uint32_t id; Byte *data; } Form;

static Byte *image, *index_header, *map_table;
static Byte *plugin_source;
static Form forms[2048];
static size_t form_count;
static uint32_t map_indices[2048];
static Row rows[5121];
static Tree primary, other;
static const char *scenario;

static void check(int ok, const char *reason)
{
    if (!ok) {
        fprintf(stderr, "census-fixture: %s\n", reason);
        exit(2);
    }
}

static void word(Byte *p, uint16_t value) { memcpy(p, &value, sizeof(value)); }
static void dword(Byte *p, uint32_t value) { memcpy(p, &value, sizeof(value)); }
static void qword(Byte *p, uint64_t value) { memcpy(p, &value, sizeof(value)); }
static void address(Byte *p, const Byte *value) { qword(p, (uintptr_t)value); }
static void set_key(Byte *p, Key key) { qword(p, key.high); qword(p + 8, key.low); }
static int mode(const char *name) { return strcmp(scenario, name) == 0; }

static uint32_t read_dword(const Byte *p)
{
    uint32_t result;
    memcpy(&result, p, sizeof(result));
    return result;
}

static Byte *heap(size_t size)
{
    Byte *result = calloc(1, size);
    check(result != NULL, "heap allocation");
    return result;
}

static Byte *page(void)
{
    Byte *result = VirtualAlloc(NULL, 4096, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    check(result != NULL, "page allocation");
    return result;
}

static int compare_rows(const void *left, const void *right)
{
    const Row *a = left, *b = right;
    if (a->key.high != b->key.high) return a->key.high > b->key.high ? 1 : -1;
    return (a->key.low > b->key.low) - (a->key.low < b->key.low);
}

static uint64_t key_first(uint32_t owner, uint32_t discriminator)
{
    return (uint64_t)owner << 32 | 0x10000 | discriminator;
}

static Byte *new_form(uint32_t id, Byte type, size_t size)
{
    check(form_count < _countof(forms), "form storage capacity");
    Byte *form = heap(size);
    dword(form + 0x28, id);
    form[0x2e] = type;
    forms[form_count++] = (Form){id, form};
    return form;
}

static void publish_identity(void)
{
    Byte *handler = heap(0x15b0), *slot = heap(8);
    Byte *source_index = heap(8), *vector = heap(16), *source_entry = heap(8);
    plugin_source = heap(0x370);
    address(plugin_source, image + 0x4b29b80);
    memcpy(plugin_source + 0x38, "fixture.esm", sizeof("fixture.esm"));
    char directory[MAX_PATH];
    DWORD length = GetModuleFileNameA(NULL, directory, MAX_PATH);
    check(length > 0 && length < MAX_PATH, "owned plugin directory");
    char *filename = strrchr(directory, '\\');
    check(filename != NULL, "owned plugin path");
    *filename = '\0';
    memcpy(plugin_source + 0x268, directory, (size_t)(filename - directory) + 1);
    if (mode("relative-data")) {
        memset(plugin_source + 0x268, 0, 260);
        memcpy(plugin_source + 0x268, "DATA\\", sizeof("DATA\\"));
    }
    dword(plugin_source + 0x1b8, 1);
    address(handler + 0x1570, plugin_source);
    dword(handler + 0x1580, 1);
    dword(handler + 0x1584, 1);
    address(handler + 0x1588, slot);
    address(slot, plugin_source);
    address(image + 0x5fd9b28, handler);
    dword(image + 0x5e881e8, 1);
    address(image + 0x5e881f0, source_index);
    address(source_index, vector);
    address(vector, source_entry);
    dword(vector + 8, 1);
    address(source_entry, plugin_source);
}

static uint32_t home(uint32_t id)
{
    uint64_t hash = 0xcbf29ce484222325;
    for (int i = 0; i < 4; ++i, id >>= 8) {
        hash ^= id & 255;
        hash *= 0x100000001b3;
    }
    return (uint32_t)(hash % MAP_CAP);
}

static Byte *bucket(uint32_t index)
{
    check(index < MAP_CAP, "bucket index");
    return map_table + 0x18 * index;
}

static void make_forms(size_t target_count)
{
    size_t owner_count = (target_count + 11) / 12;
    for (uint32_t i = 0; i < owner_count + 1; ++i) {
        uint32_t id = i == owner_count ? EXCEPTIONAL_OWNER : OWNER + i;
        Byte *form = new_form(id, 0xba, 0x58);
        dword(form + 0x50, id * 17);
        dword(form + 0x54, id);
    }
    Byte *rsgds[5];
    for (unsigned i = 0; i < _countof(rsgds); ++i) rsgds[i] = new_form(RSGD + i, 0xab, 0x32);
    for (unsigned i = 0; i < 13; ++i) {
        Byte *form = new_form(BIOM + i, 0xa0, 0x318);
        Byte *list = heap(16);
        dword(form + 0x308, 2);
        address(form + 0x310, list);
        address(list, rsgds[i % 5]);
        address(list + 8, rsgds[(i + 1) % 5]);
    }
    for (unsigned i = 0; i < 64; ++i) {
        Byte *form = new_form(RESOURCE + i, 0x9f, 0x118);
        address(form, image + 0x4b6f0b0);
    }

    // Reserve all home buckets first. Allocate collisions from other free buckets.
    Byte *map = heap(0x30);
    map_table = heap(MAP_CAP * 0x18);
    address(map + 0x10, map_table);
    qword(map + 0x18, MAP_CAP);
    address(image + 0x5e60ea0, map);
    Byte *reserved = heap(MAP_CAP);
    for (size_t i = 0; i < form_count; ++i) reserved[home(forms[i].id)] = 1;
    for (uint32_t i = 0; i < MAP_CAP; ++i) dword(bucket(i) + 0x10, UINT32_MAX);
    uint32_t free_index = MAP_CAP;
    for (size_t i = 0; i < form_count; ++i) {
        uint32_t index = home(forms[i].id);
        if (read_dword(bucket(index) + 0x10) != UINT32_MAX) {
            while (read_dword(bucket(index) + 0x10) != MAP_CAP) index = read_dword(bucket(index) + 0x10);
            do {
                check(free_index > 0, "map collision overflow");
                --free_index;
            } while (reserved[free_index]);
            dword(bucket(index) + 0x10, free_index);
            index = free_index;
        }
        map_indices[i] = index;
        dword(bucket(index), forms[i].id);
        address(bucket(index) + 8, forms[i].data);
        dword(bucket(index) + 0x10, MAP_CAP);
    }
    free(reserved);

    if (mode("map-alias")) {
        address(bucket(map_indices[1]) + 8, forms[0].data);
    }
    if (mode("bad-owner-key")) dword(forms[0].data + 0x54, OWNER + 1);
    if (mode("bad-biome-type")) {
        for (size_t i = 0; i < form_count; ++i) {
            if (forms[i].id == BIOM) forms[i].data[0x2e] = 0xba;
        }
    }
    if (mode("bad-resource-vptr") || mode("bad-resource-type")) {
        for (size_t i = 0; i < form_count; ++i) {
            if (forms[i].id == RESOURCE + 1) {
                if (mode("bad-resource-type")) forms[i].data[0x2e] = 0xab;
                else address(forms[i].data, image + 0x4b6f0b8);
            }
        }
    }
    if (mode("bad-rsgd-list")) {
        for (size_t i = 0; i < form_count; ++i) {
            if (forms[i].id == BIOM) {
                Byte *decoy = heap(0x30);
                dword(decoy + 0x28, RSGD);
                Byte *list = heap(8);
                address(list, decoy);
                address(forms[i].data + 0x310, list);
                dword(forms[i].data + 0x308, 1);
            }
        }
    }
    if (mode("map-table-edge")) {
        address(bucket(map_indices[1]) + 8, bucket(map_indices[0]));
    }
    if (mode("map-cycle")) {
        dword(bucket(map_indices[1]) + 0x10, map_indices[1]);
    }
    if (mode("map-sentinel")) {
        dword(bucket(map_indices[1]) + 0x10, MAP_CAP + 2);
    }
    if (mode("map-region-crossing")) {
        Byte *reservation = VirtualAlloc(NULL, (size_t)MAP_CAP * 0x18 + 8192, MEM_RESERVE, PAGE_NOACCESS);
        check(reservation != NULL, "reserve map extent");
        size_t entry = (size_t)home(OWNER) * 0x18;
        size_t alignment = ((4096 - 8) + 4096 - entry % 4096) % 4096;
        Byte *pages = reservation + alignment + entry - (4096 - 8);
        check(VirtualAlloc(pages, 8192, MEM_COMMIT, PAGE_READWRITE) == pages, "commit map boundary");
        DWORD previous;
        check(VirtualProtect(pages + 4096, 4096, PAGE_READONLY, &previous) != 0, "split map boundary");
        address(map + 0x10, reservation + alignment);
    }
    if (mode("map-duplicate") || mode("decoy-invalid") || mode("decoy-valid") || mode("long-chain")) {
        unsigned length = mode("long-chain") ? 255 : 1;
        uint32_t tail = map_indices[1];
        while (read_dword(bucket(tail) + 0x10) != MAP_CAP) tail = read_dword(bucket(tail) + 0x10);
        for (unsigned i = 0; i < length; ++i) {
            do {
                check(free_index > 0, "map forced collision overflow");
                --free_index;
            } while (reserved[free_index]);
            dword(bucket(tail) + 0x10, free_index);
            tail = free_index;
            uint32_t key = 0x680000 + i;
            Byte *decoy = NULL;
            if (mode("map-duplicate")) {
                key = forms[1].id;
                decoy = forms[1].data;
            } else {
                decoy = new_form(key + (mode("decoy-invalid") ? 1u : 0u), 0x20, 0x30);
            }
            dword(bucket(tail), key);
            address(bucket(tail) + 8, decoy);
            dword(bucket(tail) + 0x10, MAP_CAP);
        }
    }
}

static void make_rows(size_t targets, size_t mixed)
{
    for (size_t i = 0; i < targets; ++i) {
        uint32_t owner = i + 1 == targets ? EXCEPTIONAL_OWNER : OWNER + (uint32_t)(i / 12);
        Row *row = &rows[i];
        row->key = (Key){key_first(owner, DISC), BIOM + i % 12};
        row->width = 0x90;
        if (i % 17) {
            row->slots[0] = RESOURCE + (uint32_t)(i % 64);
            row->slots[2] = RESOURCE + (uint32_t)((i + 1) % 64);
            row->slots[6] = RESOURCE + (uint32_t)((i + 2) % 64);
        }
    }
    for (size_t i = 0; i < mixed; ++i) {
        uint32_t owner = OWNER + (uint32_t)(i % ((targets + 11) / 12));
        Row *row = &rows[targets + i];
        row->key = (Key){key_first(owner, DISC + 1), 0xfeed0000 + i};
        row->width = i % 2 ? 0x20 : 0x38;
    }
    qsort(rows, targets + mixed, sizeof(*rows), compare_rows);
}

static Node packed(Tree *tree, size_t first, unsigned count, unsigned gap)
{
    Byte *base = page();
    ++tree->windows;
    ++tree->blocks;
    if (!tree->first_block) tree->first_block = base;
    unsigned cursor = BLOCK_END;
    dword(base, UINT32_MAX);
    dword(base + 4, count);
    word(base + 8, (uint16_t)(0x10 + 4 * count));
    word(base + 10, (uint16_t)gap);
    for (unsigned slot = 0; slot < count; ++slot) {
        const Row *row = &rows[first + slot];
        cursor -= row->width;
        if (slot == count - 1) cursor -= gap;
        check(cursor >= 0x10 + count * 4, "packed fixture layout");
        word(base + 0x10 + 4 * slot, (uint16_t)row->width);
        word(base + 0x12 + 4 * slot, (uint16_t)cursor);
        Byte *edge = base + cursor;
        set_key(edge + 0x10, row->key);
        if (row->width != 0x90) {
            address(edge, image + 0x4b3d260);
            continue;
        }
        address(edge, image + (mode("wrapper") && first + slot == 0 ? 0x4b3d260 : 0x4b3d258));
        dword(edge + 0x60, (uint32_t)row->key.low);
        dword(edge + 0x64, 0x3f800000);
        dword(edge + 0x68, (uint32_t)(row->key.low * 313));
        if (row->key.low % 2) dword(edge + 0x6c, RSGD);
        memcpy(edge + 0x70, row->slots, sizeof(row->slots));
        tree->edges[first + slot] = edge;
    }
    dword(base + 12, cursor);
    return (Node){base, rows[first].key};
}

static Node combine(Tree *tree, const Node *nodes, size_t count, unsigned level)
{
    Byte *base = page();
    ++tree->windows;
    dword(base, level);
    dword(base + 4, (uint32_t)(level ? count - 1 : count));
    if (!level) ++tree->leaves;
    if (level && count > 1 && !tree->first_branch) tree->first_branch = base;
    for (unsigned i = 0; i < count; ++i) {
        unsigned key_base = level ? 0x8 : 0x18;
        unsigned pointer_base = level ? 0xa88 : 0xa98;
        if (!level || i) set_key(base + key_base + (i - (level != 0)) * 16, nodes[i].minimum);
        address(base + pointer_base + i * 8, nodes[i].page);
    }
    return (Node){base, nodes[0].minimum};
}

static void build_tree(Tree *tree, size_t count, unsigned block_width, unsigned leaf_width, unsigned min_depth)
{
    tree->count = count;
    if (!count) return;
    tree->edges = (Byte **)heap(count * sizeof(Byte *));
    Node *nodes = (Node *)heap(count * sizeof(*nodes));
    size_t blocks = 0;
    for (size_t first = 0; first < count; first += block_width) {
        unsigned here = (unsigned)(count - first);
        if (here > block_width) here = block_width;
        unsigned hole = mode("holes") || mode("bad-hole") ? 16 : 0;
        nodes[blocks++] = packed(tree, first, here, hole);
    }
    if (!leaf_width) {
        check(blocks == 1, "direct root count");
        tree->root = nodes[0];
        free(nodes);
        return;
    }
    Byte *previous = NULL;
    size_t leaves = 0;
    for (size_t first = 0; first < blocks; first += leaf_width) {
        size_t here = blocks - first < leaf_width ? blocks - first : leaf_width;
        Node leaf = combine(tree, nodes + first, here, 0);
        if (previous) address(previous + 8, leaf.page);
        else tree->first_leaf = leaf.page;
        address(leaf.page + 0x10, previous);
        previous = leaf.page;
        nodes[leaves++] = leaf;
    }
    size_t layer = leaves;
    unsigned depth = 0;
    while (layer > 1 || depth < min_depth) {
        size_t parents = 0;
        ++depth;
        for (size_t first = 0; first < layer; first += 4) {
            size_t here = layer - first < 4 ? layer - first : 4;
            nodes[parents++] = combine(tree, nodes + first, here, depth);
        }
        layer = parents;
    }
    tree->depth = depth;
    tree->root = nodes[0];
    free(nodes);
}

static void publish(const Tree *tree)
{
    address(index_header, tree->root.page);
    qword(index_header + 0x48, tree->count);
}

static void slots(Tree *tree, int restored)
{
    static const uint32_t zero[7] = {0};
    for (size_t i = 0; i < tree->count; ++i) {
        if (tree->edges[i]) memcpy(tree->edges[i] + 0x70, restored ? rows[i].slots : zero, sizeof(zero));
    }
}

static void truth(void)
{
    printf("TRUTH %zu %zu %zu %zu %zu\n",
           primary.count, primary.windows, primary.blocks, primary.leaves, primary.depth);
    for (size_t i = 0; i < primary.count; ++i) {
        const Row *row = &rows[i];
        printf("%" PRIu64 " %" PRIu64 " %u", row->key.high, row->key.low, row->width);
        for (unsigned slot = 0; slot < 7; ++slot) printf(" %" PRIu32, row->slots[slot]);
        putchar('\n');
    }
}

static void build(void)
{
    image = (Byte *)GetModuleHandleW(NULL);
    check((uintptr_t)image_tail <= (uintptr_t)(image + 0x4b3d258) &&
          (uintptr_t)(image + 0x82eec30) < (uintptr_t)(image_tail + sizeof(image_tail)),
          "synthetic image extent");
    Byte *context = image + 0x82ee5c0;
    index_header = context + 0x300;
    Byte *receiver = heap(0x108), *registry = heap(64 * 0x18);
    address(context, image + 0x4d6a6c0);
    address(image + 0x82eebb0, context);
    address(receiver, image + 0x4d5fac8);
    address(image + 0x61fa160, receiver);
    word(image + 0x61dfa4c, DISC);
    dword(image + 0x82eec20, 64);
    address(image + 0x82eec28, registry);
    address(registry + 0x18 * DISC, receiver + 0x100);
    publish_identity();

    size_t targets = 36, mixed = 12;
    unsigned block_width = 7, leaf_width = 2, min_depth = 2;
    if (mode("empty")) targets = mixed = 0;
    if (mode("direct") || mode("all-seven") || mode("holes") || mode("bad-hole") || mode("wrapper") ||
        mode("reuse") || mode("wrong-type") || mode("blank-mixed") || mode("namespace-invalid") ||
        mode("source-filtered") || mode("source-unreadable") || mode("map-region-crossing") || mode("relative-data")) {
        targets = 4;
        mixed = 2;
        block_width = 16;
        leaf_width = min_depth = 0;
    }
    if (mode("corpus")) {
        targets = 3210;
        mixed = 390;
        block_width = 24;
        leaf_width = 7;
        min_depth = 3;
    }
    if (mode("upper")) {
        targets = 4096;
        mixed = 1024;
        block_width = 13;
        leaf_width = 7;
        min_depth = 4;
    }
    if (mode("duplicate")) {
        targets = 2;
        mixed = 0;
        block_width = leaf_width = 1;
        min_depth = 1;
    }
    make_forms(targets);
    if (mode("source-filtered")) word(forms[0].data + 0x30, UINT16_MAX);
    if (mode("source-unreadable")) {
        Byte *unreadable = VirtualAlloc(NULL, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_NOACCESS);
        check(unreadable != NULL, "reserve unavailable source history");
        address(image + 0x5e881f0, unreadable);
    }
    make_rows(targets, mixed);
    if (mode("all-seven")) {
        for (unsigned lane = 0; lane < 7; ++lane) rows[1].slots[lane] = RESOURCE + lane;
    }
    if (mode("duplicate")) rows[1] = rows[0];
    build_tree(&primary, targets + mixed, block_width, leaf_width, min_depth);
    publish(&primary);
    if (mode("switch")) {
        build_tree(&other, primary.count, block_width - 1, leaf_width, min_depth);
    }
    if (mode("insert")) {
        rows[primary.count] = (Row){{key_first(EXCEPTIONAL_OWNER, DISC + 1), 1}, 0x20, {0}};
        build_tree(&other, primary.count + 1, block_width, leaf_width, min_depth);
    }
    if (mode("remove")) {
        build_tree(&other, primary.count - 1, block_width, leaf_width, min_depth);
    }
    if (mode("bad-hole")) word(primary.first_block + 10, 15);
    if (mode("bad-count")) qword(index_header + 0x48, primary.count + 1);
    if (mode("bad-span")) word(primary.first_block + 0x12, 0x11);
    if (mode("bad-biom")) dword(primary.edges[0] + 0x60, BIOM + 1);
    if (mode("namespace-invalid")) plugin_source[0x218] = 0xff;
    if (mode("optional-absent")) dword(primary.edges[0] + 0x6c, 0x750000);
    if (mode("bad-fence")) set_key(primary.first_branch + 8, (Key){1, 1});
    if (mode("bad-minimum")) set_key(primary.first_leaf + 0x18, (Key){1, 1});
    if (mode("bad-link")) address(primary.first_leaf + 8, primary.first_leaf);
    if (mode("cycle")) address(primary.root.page + 0xa88, primary.root.page);
    if (mode("bad-level")) dword(primary.root.page, 5);
    if (mode("bad-child")) address(primary.root.page + 0xa88, primary.first_block);
    if (mode("alias-child")) {
        uint64_t first;
        memcpy(&first, primary.first_branch + 0xa88, sizeof(first));
        qword(primary.first_branch + 0xa90, first);
    }
    if (mode("wrong-type")) {
        // Give a mixed row the target vptr without changing its discriminator.
        Byte *base = primary.first_block;
        uint16_t offset;
        memcpy(&offset, base + 0x12 + 3 * 4, sizeof(offset));
        address(base + offset, image + 0x4b3d258);
    }
    if (mode("blank-mixed")) {
        for (size_t i = 0; i < primary.count; ++i) {
            if (!primary.edges[i]) {
                // The first block in this scenario holds all records.
                uint16_t offset;
                memcpy(&offset, primary.first_block + 0x12 + i * 4, sizeof(offset));
                qword(primary.first_block + offset, 0);
                break;
            }
        }
    }
    if (mode("unreadable")) {
        DWORD previous;
        check(VirtualProtect(primary.first_block, 4096, PAGE_NOACCESS, &previous) != 0, "protect block");
    }
    if (mode("region-crossing")) {
        Byte *pair = VirtualAlloc(NULL, 8192, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
        DWORD previous;
        check(pair != NULL, "reserve two pages");
        memcpy(pair + 2048, primary.first_block, BLOCK_END);
        check(VirtualProtect(pair + 4096, 4096, PAGE_READONLY, &previous) != 0, "split readable regions");
        address(index_header, pair + 2048);
    }
}

int main(int argc, char **argv)
{
    check(argc == 2, "specify a scenario");
    scenario = argv[1];
    build();
    setvbuf(stdout, NULL, _IONBF, 0);
    puts("READY");
    char command[32];
    while (fgets(command, sizeof(command), stdin)) {
        command[strcspn(command, "\r\n")] = '\0';
        if (!strcmp(command, "quit")) return 0;
        if (!strcmp(command, "truth")) truth();
        else if (!strcmp(command, "clear")) slots(&primary, 0);
        else if (!strcmp(command, "namespace-drift"))
            memcpy(plugin_source + 0x38, "drifted.esm", sizeof("drifted.esm"));
        else if (!strcmp(command, "vector-drift")) word(forms[0].data + 0x30, UINT16_MAX);
        else if (!strcmp(command, "input-drift-clear")) {
            dword(forms[0].data + 0x50, 13);
            slots(&primary, 0);
        }
        else if (!strcmp(command, "restore")) slots(&primary, 1);
        else if (!strcmp(command, "repack") || !strcmp(command, "insert") ||
                 !strcmp(command, "remove")) {
            check(other.root.page != NULL, "no alternate graph for scenario");
            publish(&other);
        }
        else if (!strcmp(command, "reuse")) {
            Byte *edge = primary.edges[primary.count - 1];
            check(edge != NULL, "last descriptor has no typed storage");
            qword(edge + 0x18, BIOM + 12);
            dword(edge + 0x60, BIOM + 12);
        } else if (!strcmp(command, "aba")) {
            slots(&primary, 0);
            if (other.root.page) publish(&other);
            Sleep(1);
            publish(&primary);
            slots(&primary, 1);
        } else check(0, "unknown command");
        puts("ACK");
    }
    return 0;
}
