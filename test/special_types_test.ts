const bridge = globalThis[Symbol.for('systemservice')];
const NativeSpecialTypesTest = bridge.special_types_test;

export interface CustomTableType {
  field: number;
}

export const specialTypesTest = {
  array(arrayVal: any[]): Promise<void> {
    return NativeSpecialTypesTest.array(arrayVal);
  },

  unspec(unspecVal: any): Promise<void> {
    return NativeSpecialTypesTest.unspec(unspecVal);
  },

  table(tableVal: CustomTableType): Promise<void> {
    return NativeSpecialTypesTest.table(tableVal);
  },

  allSpecial(arrayVal: any[], unspecVal: any, tableVal: CustomTableType): Promise<void> {
    return NativeSpecialTypesTest.all_special(arrayVal, unspecVal, tableVal);
  },
};