#!/usr/bin/env python3
"""Minimal Python ctypes integration example for Arcane-Nexus SDK."""
import ctypes
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_PATH = os.environ.get("ARCANE_NEXUS_LIB", os.path.join(ROOT, "lib", "libarcane_nexus.so"))

lib = ctypes.CDLL(LIB_PATH)
lib.InitializeSDK.argtypes = [ctypes.c_char_p]
lib.InitializeSDK.restype = ctypes.c_int
lib.ShutdownSDK.argtypes = []
lib.StoreMemory.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.StoreMemory.restype = ctypes.c_int
lib.RecallMemory.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)
]
lib.RecallMemory.restype = ctypes.c_int
lib.ProcessBatchRelay.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int
]
lib.ProcessBatchRelay.restype = ctypes.c_int
lib.DeleteMemory.argtypes = [ctypes.c_char_p]
lib.DeleteMemory.restype = ctypes.c_int

assert lib.InitializeSDK(None) == 0

# 1. Hard-write knowledge node
lib.StoreMemory(b"Brand", b"profile", "Micro-String / 玄樞 SDK".encode("utf-8"), 2)

# 2. Memory-First recall
buf = ctypes.create_string_buffer(8192)
hit = ctypes.c_int(0)
lib.RecallMemory("玄樞".encode("utf-8"), b"", buf, len(buf), ctypes.byref(hit))
print(f"Recall hit={hit.value}:\n{buf.value.decode('utf-8')}")

# 3. Long-task 10K batch relay
lib.ProcessBatchRelay(b"LongTask_01", b"task_flow", "批次一：完成環境檢查".encode("utf-8"), buf, len(buf))
print("Relay output:\n" + buf.value.decode("utf-8"))

# 4. Recycle slot & zero-disk shutdown
lib.DeleteMemory(b"Brand")
lib.ShutdownSDK()
print("Python example finished cleanly.")
