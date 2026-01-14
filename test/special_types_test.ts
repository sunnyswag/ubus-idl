const bridge = globalThis[Symbol.for('systemservice')];
const NativeSpecialTypesTest = bridge.special_types_test;

export interface CustomTableType {
  field: number;
}

export const specialTypesTest = {
  array(array_val: any[]): Promise<void> {
    return NativeSpecialTypesTest.array(array_val);
  },

  unspec(unspec_val: any): Promise<void> {
    return NativeSpecialTypesTest.unspec(unspec_val);
  },

  table(table_val: CustomTableType): Promise<void> {
    return NativeSpecialTypesTest.table(table_val);
  },

  all_special(array_val: any[], unspec_val: any, table_val: CustomTableType): Promise<void> {
    return NativeSpecialTypesTest.all_special(array_val, unspec_val, table_val);
  },
};