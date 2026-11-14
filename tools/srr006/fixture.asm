; Original synthetic target with the frame relationships used by SRR-005.
option casemap:none

EXTERN fixture_count:DWORD
EXTERN fixture_guard:QWORD

.code
PUBLIC guard_site, iterator_site, callback_site, allocator_site
PUBLIC early_return, later_return, iterator_return, callback_return, adapter_return
PUBLIC sweep_early, sweep_later, sample_guard, fixture_other_callback, fixture_end

sample_guard PROC
guard_site LABEL BYTE
    cmp QWORD PTR [fixture_guard], rsi
    lock inc DWORD PTR [fixture_count]
    ret
sample_guard ENDP

sweep_early PROC FRAME
    sub rsp, 28h
    .allocstack 28h
    .endprolog
    call iterator
early_return LABEL BYTE
    add rsp, 28h
    ret
sweep_early ENDP

sweep_later PROC FRAME
    sub rsp, 28h
    .allocstack 28h
    .endprolog
    call iterator
later_return LABEL BYTE
    add rsp, 28h
    ret
sweep_later ENDP

iterator PROC FRAME
    push r14
    .pushreg r14
    sub rsp, 30h
    .allocstack 30h
    .endprolog
    mov r14, rcx
    mov rax, [rcx]
iterator_site LABEL BYTE
    call QWORD PTR [rax+10h]
iterator_return LABEL BYTE
    add rsp, 30h
    pop r14
    ret
iterator ENDP

callback PROC FRAME
callback_site LABEL BYTE
    sub rsp, 28h
    .allocstack 28h
    .endprolog
    lock inc DWORD PTR [fixture_count]
    cmp BYTE PTR [rdx+2eh], 0bah
    jne callback_done
    mov rcx, rdx
    call adapter
callback_return LABEL BYTE
callback_done:
    add rsp, 28h
    ret
callback ENDP

adapter PROC FRAME
    push rbx
    .pushreg rbx
    push rbp
    .pushreg rbp
    push rsi
    .pushreg rsi
    push rdi
    .pushreg rdi
    push r12
    .pushreg r12
    push r14
    .pushreg r14
    push r15
    .pushreg r15
    sub rsp, 40h
    .allocstack 40h
    .endprolog
    mov QWORD PTR [rsp+90h], rcx
    mov QWORD PTR [rsp+88h], 0
    lea rcx, [rsp+90h]
    lea rdx, [rsp+88h]
    call allocator
adapter_return LABEL BYTE
    add rsp, 40h
    pop r15
    pop r14
    pop r12
    pop rdi
    pop rsi
    pop rbp
    pop rbx
    ret
adapter ENDP

allocator PROC
allocator_site LABEL BYTE
    lock inc DWORD PTR [fixture_count]
    ret
allocator ENDP

fixture_other_callback PROC
    lock inc DWORD PTR [fixture_count]
    ret
fixture_other_callback ENDP

fixture_end LABEL BYTE
END
