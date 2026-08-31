
longlong * FUN_141580660(undefined8 *param_1,longlong *param_2,undefined1 param_3)

{
  uint uVar1;
  uint *puVar2;
  longlong lVar3;
  float *pfVar4;
  longlong *plVar5;
  longlong *plVar6;
  longlong lVar7;
  longlong *plVar8;
  undefined8 uVar9;
  float fVar10;
  int local_res8 [2];
  ulonglong local_res10;
  undefined1 local_res18 [8];
  undefined4 local_res20 [2];
  float local_98 [2];
  undefined8 local_90;
  undefined8 local_88;
  undefined8 local_80 [2];
  undefined8 local_70 [2];
  undefined1 *local_60;
  undefined4 *local_58;
  undefined8 local_50;
  float *local_48;
  longlong *local_40;
  
  *param_2 = 0;
  param_2[1] = 0;
  puVar2 = (uint *)*param_1;
  local_res20[0] = 0;
  local_res18[0] = param_3;
  pfVar4 = (float *)thunk_FUN_144d8c490(&local_88);
  fVar10 = *pfVar4;
  uVar9 = thunk_FUN_140924800(puVar2);
  local_60 = local_res18;
  local_58 = local_res20;
  local_50 = param_1[1];
  local_48 = local_98;
  local_98[0] = (float)uVar9 * (pfVar4[1] - fVar10) + fVar10;
  local_40 = param_2;
  if (*(longlong *)param_1[2] == 0) {
    lVar7 = *param_2;
  }
  else {
    plVar5 = FUN_14157c470(&local_60,local_80,*(longlong *)param_1[2]);
    lVar7 = *plVar5;
    *param_2 = lVar7;
    param_2[1] = plVar5[1];
  }
  if ((lVar7 == 0) && (param_2[1] == 0)) {
    uVar1 = *(uint *)(*(longlong *)param_1[3] + 0x728);
    if (uVar1 != 0) {
      plVar8 = *(longlong **)(*(longlong *)param_1[3] + 0x730);
      plVar5 = plVar8 + uVar1;
      for (; plVar8 != plVar5; plVar8 = plVar8 + 1) {
        local_res8[0] = 0;
        if ((plVar8 == (longlong *)0x0) && (thunk_FUN_144d76220(local_res8), local_res8[0] != 0)) {
          local_res10 = 0;
          DAT_00000000 = 0;
        }
        local_res10 = local_res10 & 0xffffffff00000000;
        if (((DAT_14bc65518 != '\0') && (*plVar8 != 0)) &&
           (uVar9 = thunk_FUN_140f116b0(plVar8), (char)uVar9 != '\0')) {
          thunk_FUN_144d76220((undefined4 *)&local_res10);
          if ((int)local_res10 != 0) {
            local_90 = 0;
            DAT_00000000 = 0;
          }
        }
        plVar6 = FUN_14157c470(&local_60,local_70,*plVar8);
        lVar7 = *plVar6;
        *param_2 = lVar7;
        lVar3 = plVar6[1];
        param_2[1] = lVar3;
        if ((lVar7 != 0) && (lVar3 != 0)) {
          return param_2;
        }
      }
    }
  }
  return param_2;
}

