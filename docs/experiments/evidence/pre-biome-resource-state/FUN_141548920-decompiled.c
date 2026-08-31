
bool FUN_141548920(uint *param_1,longlong *param_2)

{
  longlong *plVar1;
  uint uVar2;
  longlong lVar3;
  uint *puVar4;
  longlong lVar5;
  undefined8 uVar6;
  longlong *plVar7;
  longlong *plVar8;
  longlong *plVar9;
  int local_res8 [2];
  ulonglong local_res18;
  int local_res20 [2];
  int local_48;
  int local_44;
  undefined8 local_40;
  
  if (*param_1 == 0) {
    return true;
  }
  plVar9 = *(longlong **)(param_1 + 2);
  plVar1 = plVar9 + *param_1;
  if (plVar9 == plVar1) {
    return true;
  }
  do {
    local_res8[0] = 0;
    if ((plVar9 == (longlong *)0x0) && (thunk_FUN_144d76220(local_res8), local_res8[0] != 0)) {
      local_res18 = 0;
      DAT_00000000 = 0;
    }
    local_res18 = local_res18 & 0xffffffff00000000;
    if (((DAT_14bc65518 != '\0') && (*plVar9 != 0)) &&
       (uVar6 = thunk_FUN_140f116b0(plVar9), (char)uVar6 != '\0')) {
      thunk_FUN_144d76220((undefined4 *)&local_res18);
      if ((int)local_res18 != 0) {
        local_40 = 0;
        DAT_00000000 = 0;
      }
    }
    lVar3 = *param_2;
    puVar4 = (uint *)param_2[1];
    uVar2 = *(uint *)(*plVar9 + 0x118);
    if (uVar2 != 0) {
      plVar7 = *(longlong **)(*plVar9 + 0x120);
      plVar8 = plVar7 + (ulonglong)uVar2 * 0x47;
      for (; plVar7 != plVar8; plVar7 = plVar7 + 0x47) {
        local_res20[0] = 0;
        if ((plVar7 == (longlong *)0x0) && (thunk_FUN_144d76220(local_res20), local_res20[0] != 0))
        {
          local_40 = 0;
          DAT_00000000 = 0;
        }
        local_48 = 0;
        if (((DAT_14bc65518 != '\0') && (*plVar7 != 0)) &&
           ((uVar6 = thunk_FUN_140f11690(plVar7), (char)uVar6 != '\0' &&
            (thunk_FUN_144d76220(&local_48), local_48 != 0)))) {
          local_40 = 0;
          DAT_00000000 = 0;
        }
        lVar5 = *plVar7;
        if (*(char *)(lVar5 + 0x2f8) == '\x06') {
          *(undefined4 *)(lVar3 + 0x68) = *(undefined4 *)(lVar5 + 0x70);
          local_44 = *(int *)(lVar5 + 0x70);
          thunk_FUN_141536610(puVar4,&local_44);
        }
        if (*(int *)(lVar3 + 0x68) != 0) break;
      }
    }
    if ((*(int *)(*param_2 + 0x68) != 0) || (plVar9 = plVar9 + 1, plVar9 == plVar1)) {
      return *(int *)(*param_2 + 0x68) == 0;
    }
  } while( true );
}

