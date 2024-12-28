/*
 * Copyright (C) 2020  Anthony Doud & Joel Baranick
 * All rights reserved
 *
 * SPDX-License-Identifier: GPL-2.0-only
 */

#pragma once

#include <NimBLEDevice.h>
#include "BLE_Common.h"

class BLE_Heart_Service {
 public:
  BLE_Heart_Service();
  void setupService(NimBLEServer *pServer, MyCallbacks *chrCallbacks);
  void update();

 private:
BLEService *pHeartService;
BLECharacteristic *heartRateMeasurementCharacteristic;
};