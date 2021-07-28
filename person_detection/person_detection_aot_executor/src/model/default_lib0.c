#include "../../src/standalone_crt/include/tvm/runtime/crt/internal/aot_executor/aot_executor.h"
#include "../../src/standalone_crt/include/tvm/runtime/c_runtime_api.h"
#ifdef __cplusplus
extern "C"
#endif
TVM_DLL int32_t tvmgen_default_run_model(arg0,arg1);
static int32_t __tvm_main__(void* args, void* type_code, int num_args, void* out_value, void* out_type_code, void* resource_handle) {
return tvmgen_default_run_model(((DLTensor*)(((TVMValue*)args)[0].v_handle))[0].data,((DLTensor*)(((TVMValue*)args)[1].v_handle))[0].data);
}
const tvm_model_t tvmgen_default_network = {
    .run_func = &__tvm_main__,
    .num_input_tensors = 1,
    .num_output_tensors = 1, 
};
;