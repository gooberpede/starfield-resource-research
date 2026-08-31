
undefined8 FUN_140924800(uint *param_1)

{
  uint *puVar1;
  uint uVar2;
  ulonglong uVar3;
  uint uVar4;
  ulonglong uVar5;
  uint *puVar6;
  longlong lVar7;
  float fVar8;
  undefined1 auVar9 [16];
  float fVar10;
  undefined1 auVar11 [16];
  undefined1 auVar12 [64];
  
  auVar12 = ZEXT464(0x4f800000);
  fVar8 = (float)log2f(auVar12._0_8_);
  auVar11._0_12_ = ZEXT812(0);
  auVar11._12_4_ = 0;
  auVar11 = vroundss_avx(auVar11,ZEXT416((uint)(24.0 / fVar8)),2);
  fVar10 = 1.0;
  uVar2 = (uint)auVar11._0_4_;
  auVar11 = ZEXT816(0) << 0x20;
  fVar8 = 0.0;
  if ((int)uVar2 < 1) {
    uVar2 = 1;
  }
  if (0 < (int)uVar2) {
    uVar4 = *param_1;
    uVar5 = (ulonglong)uVar2;
    do {
      if (uVar4 == 0x270) {
        lVar7 = 0x270;
        puVar6 = param_1 + 2;
        do {
          uVar2 = (puVar6[-1] ^ *puVar6) & 0x7fffffff ^ puVar6[-1];
          puVar6[0x26f] = -(uint)((uVar2 & 1) != 0) & 0x9908b0df ^ puVar6[0x18c] ^ uVar2 >> 1;
          lVar7 = lVar7 + -1;
          puVar6 = puVar6 + 1;
        } while (lVar7 != 0);
        uVar4 = *param_1;
      }
      else if (0x4df < uVar4) {
        lVar7 = 0xe3;
        uVar2 = param_1[0x271];
        puVar6 = param_1 + 0x271;
        do {
          uVar4 = (puVar6[1] ^ uVar2) & 0x7fffffff ^ uVar2;
          uVar2 = puVar6[1];
          puVar6[-0x270] = -(uint)((uVar4 & 1) != 0) & 0x9908b0df ^ puVar6[0x18d] ^ uVar4 >> 1;
          lVar7 = lVar7 + -1;
          puVar6 = puVar6 + 1;
        } while (lVar7 != 0);
        lVar7 = 0x18c;
        uVar2 = param_1[0x354];
        puVar6 = param_1 + 0x354;
        do {
          puVar1 = puVar6 + 1;
          uVar4 = (uVar2 ^ *puVar1) & 0x7fffffff ^ uVar2;
          uVar2 = *puVar1;
          puVar6[-0x270] = -(uint)((uVar4 & 1) != 0) & 0x9908b0df ^ puVar6[-0x353] ^ uVar4 >> 1;
          lVar7 = lVar7 + -1;
          puVar6 = puVar1;
        } while (lVar7 != 0);
        uVar2 = (param_1[0x4e0] ^ param_1[1]) & 0x7fffffff ^ param_1[0x4e0];
        uVar4 = 0;
        param_1[0x270] = -(uint)((uVar2 & 1) != 0) & 0x9908b0df ^ param_1[0x18d] ^ uVar2 >> 1;
        *param_1 = 0;
      }
      uVar3 = (ulonglong)uVar4;
      uVar4 = uVar4 + 1;
      uVar2 = param_1[uVar3 + 1] ^ param_1[uVar3 + 1] >> 0xb & param_1[0x4e1];
      *param_1 = uVar4;
      uVar2 = uVar2 ^ (uVar2 & 0xff3a58ad) << 7;
      uVar2 = uVar2 ^ (uVar2 & 0xffffdf8c) << 0xf;
      fVar8 = fVar8 + (float)(uVar2 >> 0x12 ^ uVar2) * fVar10;
      auVar11 = ZEXT416((uint)fVar8);
      fVar10 = fVar10 * auVar12._0_4_;
      uVar5 = uVar5 - 1;
    } while (uVar5 != 0);
  }
  auVar9._0_4_ = auVar11._0_4_ / fVar10;
  auVar9._4_12_ = auVar11._4_12_;
  return auVar9._0_8_;
}

