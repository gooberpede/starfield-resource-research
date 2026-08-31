
undefined8 * FUN_14157c470(undefined8 *param_1,undefined8 *param_2,longlong param_3)

{
  byte bVar1;
  undefined4 uVar2;
  float *pfVar3;
  longlong lVar4;
  longlong *plVar5;
  longlong lVar6;
  undefined8 uVar7;
  longlong *plVar8;
  ulonglong uVar9;
  longlong *plVar10;
  float fVar11;
  float fVar12;
  ulonglong local_res8;
  ulonglong local_res10;
  
  pfVar3 = (float *)param_1[1];
  lVar4 = param_1[2];
  plVar5 = (longlong *)param_1[4];
  bVar1 = *(byte *)*param_1;
  uVar9 = (ulonglong)bVar1;
  fVar11 = *(float *)param_1[3];
  if (*(uint *)(param_3 + 0x118) != 0) {
    plVar8 = *(longlong **)(param_3 + 0x120);
    plVar10 = plVar8 + (ulonglong)*(uint *)(param_3 + 0x118) * 0x47;
    if (plVar8 != plVar10) {
      fVar12 = 0.01;
      do {
        local_res8 = local_res8 & 0xffffffff00000000;
        if (plVar8 == (longlong *)0x0) {
          thunk_FUN_144d76220((undefined4 *)&local_res8);
          if ((int)local_res8 != 0) {
            DAT_00000000 = 0;
            local_res10 = 0;
          }
        }
        local_res10 = local_res10 & 0xffffffff00000000;
        if (((DAT_14bc65518 != '\0') && (*plVar8 != 0)) &&
           (uVar7 = thunk_FUN_140f11690(plVar8), (char)uVar7 != '\0')) {
          thunk_FUN_144d76220((undefined4 *)&local_res10);
          if ((int)local_res10 != 0) {
            local_res8 = 0;
            DAT_00000000 = 0;
          }
        }
        lVar6 = *plVar8;
        if (*(byte *)(lVar6 + 0x2f8) == bVar1) {
          *pfVar3 = fVar12 * *(float *)((longlong)plVar8 + uVar9 * 0x28 + 0x24) + *pfVar3;
          uVar2 = *(undefined4 *)(lVar6 + 0x70);
          *(float *)(lVar4 + 0x70 + uVar9 * 8) = fVar11;
          *(undefined4 *)(lVar4 + 0x6c + uVar9 * 8) = uVar2;
          if (fVar11 < *pfVar3) {
            *plVar5 = lVar6;
            plVar5[1] = (longlong)(plVar8 + 1);
            break;
          }
        }
        plVar8 = plVar8 + 0x47;
      } while (plVar8 != plVar10);
    }
  }
  uVar7 = ((undefined8 *)param_1[4])[1];
  *param_2 = *(undefined8 *)param_1[4];
  param_2[1] = uVar7;
  return param_2;
}

