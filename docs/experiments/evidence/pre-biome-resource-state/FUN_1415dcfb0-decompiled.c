
void FUN_1415dcfb0(uint *param_1,undefined **param_2,uint *param_3,uint *param_4)

{
  longlong lVar1;
  uint uVar2;
  longlong *plVar3;
  longlong lVar4;
  undefined8 *puVar5;
  char cVar6;
  undefined4 *puVar7;
  undefined8 *puVar8;
  longlong *plVar9;
  uint *puVar10;
  undefined8 uVar11;
  ulonglong uVar12;
  undefined **ppuVar13;
  char *pcVar14;
  char local_res8 [8];
  undefined **local_res10;
  int local_110;
  int local_10c;
  int local_108;
  int local_104;
  int local_100;
  int local_fc;
  int local_f8;
  undefined4 local_f4;
  longlong *local_f0;
  undefined4 *local_e8;
  uint local_e0;
  int iStack_dc;
  undefined8 uStack_d8;
  longlong local_d0;
  undefined **local_c8;
  uint *local_c0;
  longlong **local_b8;
  longlong **local_b0;
  longlong *local_a8;
  char *local_a0;
  uint *local_98;
  longlong local_90;
  longlong local_88;
  undefined **local_80;
  uint *local_78;
  longlong local_70;
  longlong local_68;
  uint *local_60;
  uint *local_58;
  char *local_50;
  longlong local_48 [2];
  
  lVar4 = *(longlong *)((longlong)ThreadLocalStoragePointer + (ulonglong)_tls_index * 8);
  pcVar14 = (char *)(lVar4 + 0x5630);
  cVar6 = *pcVar14;
  puVar10 = param_3;
  local_res10 = param_2;
  local_a0 = pcVar14;
  if (cVar6 == '\0') {
    __dyn_tls_on_demand_init();
    cVar6 = *pcVar14;
  }
  puVar7 = (undefined4 *)(lVar4 + 0x2b58);
  local_f4 = *puVar7;
  local_e8 = puVar7;
  if (cVar6 == '\0') {
    __dyn_tls_on_demand_init();
  }
  *puVar7 = 0x82;
  local_f0 = (longlong *)thunk_FUN_140e5a710(param_1[0x10]);
  if ((local_f0 == (longlong *)0x0) || ((char)local_f0[0x11] != -0x60)) {
    local_f0 = (longlong *)0x0;
  }
  local_a8 = (longlong *)thunk_FUN_140e5a710(param_1[0x13]);
  if ((local_a8 == (longlong *)0x0) || ((char)local_a8[0x11] != -0x55)) {
    local_a8 = (longlong *)0x0;
  }
  if (local_f0 == (longlong *)0x0) goto LAB_1415dd4db;
  local_b8 = &local_a8;
  local_b0 = &local_f0;
  ppuVar13 = (undefined **)CONCAT71((int7)((ulonglong)puVar10 >> 8),5);
  local_c8 = param_2;
  local_c0 = param_1;
  FUN_141580660(&local_c8,&local_70,5);
  if (((*param_4 < 8) && (local_70 != 0)) && (local_68 != 0)) {
    param_1[0x19] = *(uint *)(local_70 + 0x70);
    local_110 = *(int *)(local_70 + 0x70);
    thunk_FUN_141536610(param_4,&local_110);
  }
  if ((*param_3 < 5) && (*param_4 < 8)) {
    uVar11 = 0;
    plVar3 = FUN_141580660(&local_c8,local_48,0);
    lVar4 = *plVar3;
    lVar1 = plVar3[1];
    if ((lVar4 == 0) || (lVar1 == 0)) {
      param_1[0x14] = 0;
    }
    else {
      if (*param_3 != 0) {
        puVar8 = *(undefined8 **)(param_3 + 4);
        puVar5 = puVar8 + *param_3;
        for (; puVar8 != puVar5; puVar8 = puVar8 + 1) {
          local_10c = 0;
          if (puVar8 == (undefined8 *)0x0) {
            uVar11 = 0x5c9;
            thunk_FUN_144d76220(&local_10c);
            if (local_10c != 0) {
              DAT_00000000 = 0;
            }
          }
          puVar10 = (uint *)*puVar8;
          if (*puVar10 == *(uint *)(lVar4 + 0x70)) {
            param_1[0x14] = *puVar10;
            param_1[0x15] = puVar10[1];
            param_1[0x16] = puVar10[2];
            param_1[0x17] = puVar10[3];
            param_1[0x18] = puVar10[4];
            puVar7 = local_e8;
            goto LAB_1415dd4db;
          }
        }
      }
      param_1[0x14] = *(uint *)(lVar4 + 0x70);
      local_110 = *(int *)(lVar4 + 0x70);
      thunk_FUN_141536610(param_4,&local_110);
      local_80 = local_res10;
      uVar12 = CONCAT71((int7)((ulonglong)uVar11 >> 8),1);
      local_98 = param_1;
      local_90 = lVar4;
      local_88 = lVar1;
      local_78 = param_4;
      lVar4 = FUN_14157f120((longlong *)&local_98,lVar4,uVar12);
      uVar12 = CONCAT71((int7)(uVar12 >> 8),2);
      lVar4 = FUN_14157f120((longlong *)&local_98,lVar4,uVar12);
      uVar12 = CONCAT71((int7)(uVar12 >> 8),3);
      lVar4 = FUN_14157f120((longlong *)&local_98,lVar4,uVar12);
      FUN_14157f120((longlong *)&local_98,lVar4,CONCAT71((int7)(uVar12 >> 8),4));
      local_c8 = BSTArrayAllocatorFunctor<BSScrapArrayAllocator>::vftable;
      local_c0 = param_3;
      uVar2 = thunk_FUN_144d7baf0(param_3,(longlong *)&local_c8,param_3[1],8);
      puVar7 = local_e8;
      if (uVar2 != 0xffffffff) {
        *(uint **)(*(longlong *)(param_3 + 4) + (ulonglong)uVar2 * 8) = param_1 + 0x14;
      }
    }
    goto LAB_1415dd4db;
  }
  local_e0 = 0;
  iStack_dc = 0;
  uStack_d8 = 0;
  local_d0 = 0;
  local_res8[0] = '\0';
  if (*(uint *)(local_f0 + 0xe5) != 0) {
    plVar9 = (longlong *)local_f0[0xe6];
    plVar3 = plVar9 + *(uint *)(local_f0 + 0xe5);
    if (plVar9 != plVar3) {
      do {
        local_108 = 0;
        if (plVar9 == (longlong *)0x0) {
          ppuVar13 = (undefined **)0x4fd;
          thunk_FUN_144d76220(&local_108);
          if (local_108 != 0) {
            DAT_00000000 = 0;
          }
        }
        local_104 = 0;
        if (((DAT_14bc65518 != '\0') && (*plVar9 != 0)) &&
           (uVar11 = thunk_FUN_140f116b0(plVar9), (char)uVar11 != '\0')) {
          ppuVar13 = (undefined **)0x12a;
          thunk_FUN_144d76220(&local_104);
          if (local_104 != 0) {
            DAT_00000000 = 0;
          }
        }
        local_58 = &local_e0;
        local_50 = local_res8;
        local_60 = param_3;
        FUN_14154c710(*plVar9,&local_60);
        plVar9 = plVar9 + 1;
      } while (plVar9 != plVar3);
      if (local_res8[0] != '\0') {
        if (local_e0 == 0) {
          if (*param_3 != 0) {
            uVar2 = thunk_FUN_140d455f0(0,*param_3,(uint *)param_2);
            puVar5 = (undefined8 *)thunk_FUN_141573380(param_3,uVar2);
            goto LAB_1415dd419;
          }
        }
        else {
          uVar2 = thunk_FUN_140d455f0(0,local_e0,(uint *)param_2);
          local_100 = 0;
          if (local_e0 <= uVar2) {
            param_2 = (undefined **)0x1e8;
            thunk_FUN_144d76220(&local_100);
            if (local_100 != 0) {
              DAT_00000000 = 0;
            }
          }
          local_fc = 0;
          if (local_d0 == 0) {
            param_2 = (undefined **)0x1e9;
            thunk_FUN_144d76220(&local_fc);
            if (local_fc != 0) {
              DAT_00000000 = 0;
            }
          }
          puVar5 = (undefined8 *)(local_d0 + (ulonglong)uVar2 * 8);
LAB_1415dd419:
          puVar10 = (uint *)*puVar5;
          if (puVar10 != (uint *)0x0) {
            param_1[0x14] = *puVar10;
            param_1[0x15] = puVar10[1];
            param_1[0x16] = puVar10[2];
            param_1[0x17] = puVar10[3];
            param_1[0x18] = puVar10[4];
            ppuVar13 = param_2;
            goto LAB_1415dd472;
          }
        }
        (**(code **)(*local_f0 + 0x310))();
        ppuVar13 = (undefined **)&DAT_00000024;
        thunk_FUN_144d793f0("E:\\BuildAgent\\work\\fee57674ddcb42c9\\Genesis\\Shared\\Planet\\BGSPlanetDataManager.cpp"
                            ,0x152,0x24,
                            "No valid generated common resources. Atmosphere and Everywhere resources filled all available slots for biome %s"
                           );
      }
    }
  }
LAB_1415dd472:
  local_f8 = 0;
  if (local_d0 == 0) {
    if ((iStack_dc == 0) && (puVar7 = local_e8, local_e0 == 0)) goto LAB_1415dd4db;
    ppuVar13 = (undefined **)0x392;
    thunk_FUN_144d76220(&local_f8);
    if (local_f8 != 0) {
      DAT_00000000 = 0;
    }
    puVar7 = local_e8;
    if (local_d0 == 0) goto LAB_1415dd4db;
  }
  thunk_FUN_144d7c6b0((longlong)&local_e0,8,ppuVar13);
  puVar7 = local_e8;
LAB_1415dd4db:
  if (*local_a0 == '\0') {
    __dyn_tls_on_demand_init();
  }
  *puVar7 = local_f4;
  return;
}

