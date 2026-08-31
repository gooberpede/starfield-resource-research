
void FUN_1419fe120(longlong *param_1,ulonglong param_2)

{
  longlong lVar1;
  int local_res10 [2];
  undefined8 local_res18;
  longlong local_48 [2];
  longlong local_38;
  ulonglong local_30;
  undefined8 local_28;
  undefined8 uStack_20;
  undefined8 local_18;
  undefined8 local_10;
  
  thunk_FUN_145103600(param_1,local_48,
                      ((ulonglong)DAT_14de37c70 << 0x20 | param_2 & 0xffffffff) << 0x10);
  local_18 = 0;
  local_10 = 0xfe0;
  local_28 = 0;
  uStack_20 = 0xfc;
  if ((local_30 != 0xfe0) || (local_38 != 0)) {
    local_res10[0] = 0;
    lVar1 = thunk_FUN_140844a70(local_38,local_30);
    if (*(ushort *)(lVar1 + 0x16) != DAT_14de37c70) {
      thunk_FUN_144d76220(local_res10);
    }
    if (local_res10[0] == 2) {
      local_res18 = 0;
      DAT_00000000 = 0;
    }
    lVar1 = thunk_FUN_140844a70(local_38,local_30);
    lVar1 = thunk_FUN_140e5a710(*(int *)(lVar1 + 0x20));
    if ((lVar1 != 0) && (*(char *)(lVar1 + 0x88) == -0x53)) {
      return;
    }
  }
  thunk_FUN_1409ad4f0((longlong *)&DAT_14de437c0);
  return;
}

