
undefined8 FUN_14157e850(undefined8 param_1,longlong param_2)

{
  undefined4 uVar1;
  longlong lVar2;
  char cVar3;
  longlong lVar4;
  longlong local_res18;
  longlong local_res20;
  longlong local_48 [4];
  
  lVar2 = *(longlong *)((longlong)ThreadLocalStoragePointer + (ulonglong)_tls_index * 8);
  cVar3 = *(char *)(lVar2 + 0x5630);
  if (cVar3 == '\0') {
    __dyn_tls_on_demand_init();
    cVar3 = *(char *)(lVar2 + 0x5630);
  }
  uVar1 = *(undefined4 *)(lVar2 + 0x2b58);
  if (cVar3 == '\0') {
    __dyn_tls_on_demand_init();
  }
  *(undefined4 *)(lVar2 + 0x2b58) = 0x82;
  local_res20 = param_2;
  lVar4 = thunk_FUN_14510eee0();
  thunk_FUN_145106220((longlong *)(lVar4 + 0x238),local_48);
  local_res18 = lVar4;
  FUN_14152cbc0(&local_res20,&local_res18);
  thunk_FUN_1450ee280(local_48);
  if (*(char *)(lVar2 + 0x5630) == '\0') {
    __dyn_tls_on_demand_init();
  }
  *(undefined4 *)(lVar2 + 0x2b58) = uVar1;
  return 1;
}

