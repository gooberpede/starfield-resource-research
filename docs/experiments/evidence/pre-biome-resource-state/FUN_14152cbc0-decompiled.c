
/* WARNING: Function: __chkstk replaced with injection: alloca_probe */
/* WARNING: Removing unreachable block (ram,0x00014152d178) */

void FUN_14152cbc0(longlong *param_1,longlong *param_2)

{
  float fVar1;
  float fVar2;
  uint uVar3;
  ulonglong *puVar4;
  longlong lVar5;
  uint *puVar6;
  undefined8 uVar7;
  longlong lVar8;
  longlong *plVar9;
  int iVar10;
  int *piVar11;
  uint uVar12;
  ulonglong uVar13;
  longlong *plVar14;
  longlong **pplVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  ulonglong local_res8;
  longlong *local_res10;
  ulonglong local_res18;
  ulonglong local_res20;
  int local_1590 [2];
  uint local_1588;
  uint uStack_1584;
  undefined8 uStack_1580;
  longlong *local_1578;
  uint local_1570 [2];
  uint local_1568;
  uint uStack_1564;
  undefined8 uStack_1560;
  int *local_1558;
  int local_1550;
  int local_154c;
  int local_1548;
  int local_1544;
  int local_1540;
  int local_153c;
  int local_1538;
  int local_1534;
  int local_1530 [2];
  longlong *local_1528;
  longlong *local_1520;
  uint local_1518;
  int iStack_1514;
  undefined8 uStack_1510;
  longlong local_1508;
  undefined4 local_1500;
  undefined **local_14f8;
  uint *local_14f0;
  undefined **local_14e8;
  uint *local_14e0;
  undefined **local_14d8;
  uint *local_14d0;
  longlong *local_14c8;
  longlong local_14c0 [2];
  longlong local_14b0;
  longlong local_14a8;
  ulonglong local_14a0;
  ulonglong local_1498;
  ulonglong local_1490;
  undefined8 local_1488;
  longlong local_1480;
  uint *local_1478;
  undefined8 local_1470;
  undefined8 local_1468;
  undefined8 local_1460;
  undefined8 local_1458;
  undefined8 local_1450;
  undefined8 uStack_1448;
  undefined8 local_1440;
  undefined8 local_1438;
  undefined4 local_1428;
  uint local_1424;
  uint local_1420 [1247];
  undefined4 local_a4;
  undefined8 uStack_48;
  
  pplVar15 = &local_14c8;
  uStack_48 = 0x14152cbe3;
  local_1590[0] = 0;
  local_1588 = 0;
  uStack_1584 = 0;
  uStack_1580 = 0;
  local_1578 = (longlong *)0x0;
  local_res10 = param_2;
  if (*(int *)(*param_1 + 0x134) != 0) {
    uVar13 = CONCAT44(*(int *)(*param_1 + 0x134),(uint)DAT_14de153c4) | 0x10000;
    local_1488 = 0;
    local_14c8 = param_2;
    local_1490 = uVar13;
    thunk_FUN_145107e10(param_2,local_14c0,0,&local_1490);
    local_1498 = 0xffffffffffff;
    local_1450 = 0;
    uStack_1448 = 0xa8;
    local_1440 = 0;
    local_1438 = 0xfe0;
    local_14a0 = uVar13;
    if ((local_14a8 != 0xfe0) || (local_14b0 != 0)) {
      puVar4 = (ulonglong *)thunk_FUN_1415d2b30(local_14c8,(longlong)local_14c0);
      if ((*puVar4 <= local_14a0) && ((local_14a0 != *puVar4 || (puVar4[1] <= local_1498)))) {
        do {
          plVar14 = pplVar15[4];
          plVar9 = pplVar15[3];
          thunk_FUN_1450f1a90((longlong)plVar9);
          lVar5 = thunk_FUN_140844130((longlong)plVar9,(ulonglong)plVar14);
          local_14f8 = BSTArrayAllocatorFunctor<BSScrapArrayAllocator>::vftable;
          local_14f0 = &local_1588;
          uVar3 = thunk_FUN_144d7baf0(&local_1588,(longlong *)&local_14f8,uStack_1584,8);
          local_14f8 = BSTArrayBase::IAllocatorFunctor::vftable;
          if (uVar3 != 0xffffffff) {
            local_1578[uVar3] = lVar5 + 0x20;
          }
          plVar14 = *pplVar15;
          thunk_FUN_141576500((longlong *)(pplVar15 + 1));
          local_1470 = 0;
          local_1468 = 0xa8;
          local_1460 = 0;
          local_1458 = 0xfe0;
          if ((pplVar15[4] == (longlong *)0xfe0) && (pplVar15[3] == (longlong *)0x0)) {
LAB_14152cdd0:
            pplVar15 = (longlong **)0x0;
          }
          else {
            puVar4 = (ulonglong *)thunk_FUN_1415d2b30(plVar14,(longlong)(pplVar15 + 1));
            if ((pplVar15[5] < (longlong *)*puVar4) ||
               ((pplVar15[5] == (longlong *)*puVar4 && (pplVar15[6] < (longlong *)puVar4[1]))))
            goto LAB_14152cdd0;
          }
          param_2 = local_res10;
        } while (pplVar15 != (longlong **)0x0);
      }
    }
  }
  local_1520 = (longlong *)0x0;
  uVar3 = *(uint *)(*param_1 + 0x130);
  local_a4 = 0xffffffff;
  uVar12 = 0x1571;
  uVar13 = 1;
  do {
    uVar12 = (uVar12 >> 0x1e ^ uVar12) * 0x6c078965 + (int)uVar13;
    local_1420[uVar13 - 1] = uVar12;
    uVar13 = uVar13 + 1;
  } while (uVar13 < 0x270);
  uVar13 = 1;
  uVar12 = uVar3;
  do {
    uVar12 = (uVar12 >> 0x1e ^ uVar12) * 0x6c078965 + (int)uVar13;
    local_1420[uVar13 - 1] = uVar12;
    uVar13 = uVar13 + 1;
  } while (uVar13 < 0x270);
  local_1428 = 0x270;
  local_1528 = local_1520;
  if (local_1588 != 0) {
    local_1520 = local_1578;
    local_1528 = local_1578 + local_1588;
  }
  local_1570[0] = uVar3;
  local_1424 = uVar3;
  thunk_FUN_141560e90((longlong *)&local_1520,(longlong *)&local_1528,&local_1428);
  local_1568 = 0;
  uStack_1564 = 0;
  uStack_1560 = 0;
  local_1558 = (int *)0x0;
  local_14e8 = BSTArrayAllocatorFunctor<BSScrapArrayAllocator>::vftable;
  local_14e0 = &local_1568;
  thunk_FUN_144d7f100(&local_1568,(longlong *)&local_14e8,0,8,4);
  local_14e8 = BSTArrayBase::IAllocatorFunctor::vftable;
  lVar5 = thunk_FUN_1419fe120(param_2,(ulonglong)*(uint *)(*param_1 + 0x134));
  if (lVar5 != 0) {
    puVar6 = (uint *)thunk_FUN_141a46660(lVar5);
    if (*puVar6 != 0) {
      plVar9 = *(longlong **)(puVar6 + 2);
      plVar14 = plVar9 + *puVar6;
      for (; plVar9 != plVar14; plVar9 = plVar9 + 1) {
        local_res8 = local_res8 & 0xffffffff00000000;
        if (plVar9 == (longlong *)0x0) {
          thunk_FUN_144d76220((undefined4 *)&local_res8);
          if ((int)local_res8 != 0) {
            local_res18 = 0;
          }
        }
        local_res18 = local_res18 & 0xffffffff00000000;
        if (*plVar9 == 0) {
          thunk_FUN_144d76220((undefined4 *)&local_res18);
          if ((int)local_res18 != 0) {
            local_res20 = 0;
          }
        }
        local_res20 = local_res20 & 0xffffffff00000000;
        uVar7 = thunk_FUN_140f11690(plVar9);
        if ((char)uVar7 != '\0') {
          thunk_FUN_144d76220((undefined4 *)&local_res20);
        }
        iVar10 = *(int *)(*plVar9 + 0x70);
        if (local_1568 != 0) {
          local_1550 = 0;
          if ((local_1558 == (int *)0x0) && (thunk_FUN_144d76220(&local_1550), local_1550 != 0)) {
            DAT_00000000 = 0;
          }
          for (piVar11 = local_1558; piVar11 != local_1558 + local_1568; piVar11 = piVar11 + 1) {
            if (*piVar11 == iVar10) {
              if ((int)((longlong)piVar11 - (longlong)local_1558 >> 2) != -1) goto LAB_14152d0ec;
              break;
            }
          }
        }
        local_14d8 = BSTArrayAllocatorFunctor<BSScrapArrayAllocator>::vftable;
        local_14d0 = &local_1568;
        uVar3 = thunk_FUN_144d7baf0(&local_1568,(longlong *)&local_14d8,uStack_1564,4);
        local_14d8 = BSTArrayBase::IAllocatorFunctor::vftable;
        if (uVar3 != 0xffffffff) {
          local_1558[uVar3] = iVar10;
        }
LAB_14152d0ec:
        uVar3 = local_1570[0];
      }
    }
  }
  uVar13 = (ulonglong)local_1588;
  if ((local_1588 != 0) &&
     (plVar14 = local_1578 + uVar13, plVar9 = local_1578, local_1578 != plVar14)) {
    do {
      local_1590[0] = 0;
      if (plVar9 == (longlong *)0x0) {
        thunk_FUN_144d76220(local_1590);
      }
      lVar5 = *plVar9;
      local_1500 = 0;
      *(undefined1 (*) [16])(lVar5 + 0x50) = (undefined1  [16])0x0;
      *(undefined8 *)(lVar5 + 0x60) = 0;
      *(undefined4 *)(lVar5 + 0x68) = 0;
      lVar8 = thunk_FUN_140e5a710(*(int *)(lVar5 + 0x40));
      if ((lVar8 != 0) && (*(char *)(lVar8 + 0x88) == -0x60)) {
        local_1478 = &local_1568;
        local_1480 = lVar5;
        FUN_141548920((uint *)(lVar8 + 0x728),&local_1480);
      }
      plVar9 = plVar9 + 1;
    } while (plVar9 != plVar14);
    uVar13 = (ulonglong)local_1588;
  }
  local_1518 = 0;
  iStack_1514 = 0;
  uStack_1510 = 0;
  local_1508 = 0;
  if ((int)uVar13 != 0) {
    plVar14 = local_1578 + uVar13;
    for (plVar9 = local_1578; plVar9 != plVar14; plVar9 = plVar9 + 1) {
      local_154c = 0;
      if ((plVar9 == (longlong *)0x0) && (thunk_FUN_144d76220(&local_154c), local_154c != 0)) {
        DAT_00000000 = 0;
      }
      puVar6 = (uint *)*plVar9;
      if (uVar3 == 0) {
        uVar12 = puVar6[0x12];
        uVar13 = 1;
        local_1424 = uVar12;
        do {
          uVar12 = (uVar12 >> 0x1e ^ uVar12) * 0x6c078965 + (int)uVar13;
          local_1420[uVar13 - 1] = uVar12;
          uVar13 = uVar13 + 1;
        } while (uVar13 < 0x270);
        local_1428 = 0x270;
      }
      FUN_1415dcfb0(puVar6,(undefined **)&local_1428,&local_1518,&local_1568);
    }
  }
  uVar7 = 0;
  lVar5 = thunk_FUN_1415b2a30(param_2,(ulonglong)*(uint *)(*param_1 + 0x134),0);
  if (lVar5 == 0) {
    (**(code **)(*(longlong *)*param_1 + 0x310))();
    uVar7 = 0x22;
    thunk_FUN_144d793f0("E:\\BuildAgent\\work\\fee57674ddcb42c9\\Genesis\\Shared\\Planet\\BGSPlanetDataManager.cpp"
                        ,0x2e7,0x22,"Could not obtain biome data for planet %s 0x%08x.\n");
  }
  else {
    fVar17 = 0.0;
    fVar18 = 0.0;
    fVar16 = 100.0;
    if (local_1588 != 0) {
      plVar14 = local_1578 + local_1588;
      plVar9 = local_1578;
      if (local_1578 == plVar14) {
LAB_14152d46b:
        fVar20 = fVar16 - fVar18;
        if ((fVar17 < fVar20) && (fVar18 != fVar17)) {
          if (local_1588 == 0) goto LAB_14152d66c;
          plVar14 = local_1578 + local_1588;
          if (local_1578 != plVar14) {
            fVar18 = 1.0 / fVar18;
            fVar19 = 0.5;
            plVar9 = local_1578;
            do {
              local_1540 = 0;
              if (plVar9 == (longlong *)0x0) {
                uVar7 = 0x5c9;
                thunk_FUN_144d76220(&local_1540);
                if (local_1540 != 0) {
                  DAT_00000000 = 0;
                }
              }
              lVar5 = *plVar9;
              fVar1 = fVar18 * *(float *)(lVar5 + 0x44) * fVar20;
              iVar10 = (int)fVar1;
              *(float *)(lVar5 + 0x44) =
                   (float)(int)((uint)(fVar19 <= fVar1 - (float)iVar10) + iVar10) +
                   *(float *)(lVar5 + 0x44);
              plVar9 = plVar9 + 1;
            } while (plVar9 != plVar14);
          }
        }
      }
      else {
        do {
          local_1548 = 0;
          if (plVar9 == (longlong *)0x0) {
            uVar7 = 0x5c9;
            thunk_FUN_144d76220(&local_1548);
            if (local_1548 != 0) {
              DAT_00000000 = 0;
            }
          }
          fVar18 = fVar18 + *(float *)(*plVar9 + 0x44);
          plVar9 = plVar9 + 1;
        } while (plVar9 != plVar14);
        if (fVar18 <= fVar16) {
          if (fVar18 < fVar16) goto LAB_14152d46b;
        }
        else {
          (**(code **)(*(longlong *)*param_1 + 0x310))();
          uVar7 = 0x22;
          thunk_FUN_144d793f0("E:\\BuildAgent\\work\\fee57674ddcb42c9\\Genesis\\Shared\\Planet\\BGSPlanetDataManager.cpp"
                              ,0x2f9,0x22,
                              "Biome type totals for planet \'%s\' (%08X) exceed the maximum.");
          fVar20 = fVar18 - fVar16;
          if (local_1588 == 0) goto LAB_14152d66c;
          plVar14 = local_1578 + local_1588;
          if (local_1578 != plVar14) {
            fVar19 = 0.5;
            plVar9 = local_1578;
            do {
              local_1544 = 0;
              if (plVar9 == (longlong *)0x0) {
                uVar7 = 0x5c9;
                thunk_FUN_144d76220(&local_1544);
                if (local_1544 != 0) {
                  DAT_00000000 = 0;
                }
              }
              fVar1 = *(float *)(*plVar9 + 0x44);
              if (fVar17 < fVar1) {
                fVar2 = (fVar1 / fVar18) * fVar20;
                iVar10 = (int)fVar2;
                *(float *)(*plVar9 + 0x44) =
                     fVar1 - (float)(int)((uint)(fVar19 <= fVar2 - (float)iVar10) + iVar10);
              }
              plVar9 = plVar9 + 1;
            } while (plVar9 != plVar14);
          }
        }
      }
    }
    if (1 < local_1588) {
      if (local_1588 != 0) {
        plVar14 = local_1578 + local_1588;
        fVar18 = fVar17;
        for (plVar9 = local_1578; plVar9 != plVar14; plVar9 = plVar9 + 1) {
          local_153c = 0;
          if (plVar9 == (longlong *)0x0) {
            uVar7 = 0x5c9;
            thunk_FUN_144d76220(&local_153c);
            if (local_153c != 0) {
              DAT_00000000 = 0;
            }
          }
          fVar18 = fVar18 + *(float *)(*plVar9 + 0x44);
        }
        fVar16 = fVar16 - fVar18;
        if (fVar16 == fVar17) goto LAB_14152d66c;
      }
      iVar10 = -1;
      if (fVar17 < fVar16) {
        iVar10 = 1;
      }
      do {
        plVar14 = local_1578;
        if (local_1588 == 0) {
          plVar14 = (longlong *)0x0;
        }
        while( true ) {
          plVar9 = (longlong *)0x0;
          if (local_1588 != 0) {
            plVar9 = local_1578 + local_1588;
          }
          if ((plVar14 == plVar9) || (fVar16 == fVar17)) break;
          local_1538 = 0;
          if (plVar14 == (longlong *)0x0) {
            uVar7 = 0x5c9;
            thunk_FUN_144d76220(&local_1538);
            if (local_1538 != 0) {
              DAT_00000000 = 0;
            }
          }
          fVar18 = *(float *)(*plVar14 + 0x44);
          if (fVar17 < fVar18) {
            *(float *)(*plVar14 + 0x44) = (float)iVar10 + fVar18;
            fVar16 = fVar16 - (float)iVar10;
          }
          plVar14 = plVar14 + 1;
        }
      } while (fVar16 != fVar17);
    }
  }
LAB_14152d66c:
  local_1534 = 0;
  if (local_1508 == 0) {
    if ((iStack_1514 != 0) || (local_1518 != 0)) {
      uVar7 = 0x392;
      thunk_FUN_144d76220(&local_1534);
      if (local_1534 != 0) {
        DAT_00000000 = 0;
      }
      if (local_1508 != 0) goto LAB_14152d6b8;
    }
  }
  else {
LAB_14152d6b8:
    thunk_FUN_144d7c6b0((longlong)&local_1518,8,uVar7);
    local_1518 = 0;
  }
  local_1530[0] = 0;
  if (local_1558 == (int *)0x0) {
    if ((uStack_1564 == 0) && (local_1568 == 0)) goto LAB_14152d72c;
    uVar7 = 0x392;
    thunk_FUN_144d76220(local_1530);
    if (local_1530[0] != 0) {
      DAT_00000000 = 0;
    }
    if (local_1558 == (int *)0x0) goto LAB_14152d72c;
  }
  thunk_FUN_144d7c6b0((longlong)&local_1568,4,uVar7);
  local_1568 = 0;
LAB_14152d72c:
  local_1570[0] = 0;
  if (local_1578 == (longlong *)0x0) {
    if ((uStack_1584 == 0) && (local_1588 == 0)) {
      return;
    }
    uVar7 = 0x392;
    thunk_FUN_144d76220(local_1570);
    if (local_1570[0] != 0) {
      local_res8 = 0;
      DAT_00000000 = 0;
    }
    if (local_1578 == (longlong *)0x0) {
      return;
    }
  }
  thunk_FUN_144d7c6b0((longlong)&local_1588,8,uVar7);
  return;
}

