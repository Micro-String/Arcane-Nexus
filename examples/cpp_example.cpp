// Minimal zero-header C++23 dynamic integration example for Arcane-Nexus SDK
#include <dlfcn.h>
#include <iostream>
#include <string>

int main() {
    void* handle = ::dlopen("./lib/libarcane_nexus.so", RTLD_NOW);
    if (!handle) {
        std::cerr << "dlopen failed: " << ::dlerror() << "\n";
        return 1;
    }

    auto init_sdk = reinterpret_cast<int(*)(const char*)>(::dlsym(handle, "InitializeSDK"));
    auto shutdown_sdk = reinterpret_cast<void(*)()>(::dlsym(handle, "ShutdownSDK"));
    auto store_mem = reinterpret_cast<int(*)(const char*, const char*, const char*, int)>(::dlsym(handle, "StoreMemory"));
    auto recall_mem = reinterpret_cast<int(*)(const char*, const char*, char*, int, int*)>(::dlsym(handle, "RecallMemory"));
    auto relay_mem = reinterpret_cast<int(*)(const char*, const char*, const char*, char*, int)>(::dlsym(handle, "ProcessBatchRelay"));

    if (init_sdk(nullptr) != 0) return 2;

    store_mem("Env_Check", "ops", "Linux x86_64 C++23 Ready", 2);

    char buf[4096]{};
    int hit = 0;
    recall_mem("C++23", "", buf, sizeof(buf), &hit);
    std::cout << "Recall hit=" << hit << ":\n" << buf;

    relay_mem("Job_1", "task_flow", "Batch #1 completed", buf, sizeof(buf));
    std::cout << "Relay:\n" << buf;

    shutdown_sdk();
    ::dlclose(handle);
    return 0;
}
