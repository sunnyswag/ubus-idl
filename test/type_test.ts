const bridge = globalThis[Symbol.for('systemservice')];
const NativeTypeTest = bridge.type_test;

export const typeTest = {
  allTypes(int8Val: number, int16Val: number, int32Val: number, int64Val: number, boolVal: boolean, doubleVal: number, stringVal: string): Promise<void> {
    return NativeTypeTest.all_types(int8Val, int16Val, int32Val, int64Val, boolVal, doubleVal, stringVal);
  },

  typeWithAllTypes(int8Field: number, int16Field: number, int32Field: number, int64Field: number, boolField: boolean, doubleField: number, stringField: string, optionalInt8?: number, optionalInt16?: number, optionalInt32?: number, optionalInt64?: number, optionalBool?: boolean, optionalDouble?: number, optionalString?: string): Promise<void> {
    return NativeTypeTest.type_with_all_types(int8Field, int16Field, int32Field, int64Field, boolField, doubleField, stringField, optionalInt8, optionalInt16, optionalInt32, optionalInt64, optionalBool, optionalDouble, optionalString);
  },
};