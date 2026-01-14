const bridge = globalThis[Symbol.for('systemservice')];
const NativeTypeTest = bridge.type_test;

export const typeTest = {
  all_types(int8_val: number, int16_val: number, int32_val: number, int64_val: number, bool_val: boolean, double_val: number, string_val: string): Promise<void> {
    return NativeTypeTest.all_types(int8_val, int16_val, int32_val, int64_val, bool_val, double_val, string_val);
  },

  type_with_all_types(): Promise<TypeWithAllTypes> {
    return NativeTypeTest.type_with_all_types();
  },
};