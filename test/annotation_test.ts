const bridge = globalThis[Symbol.for('systemservice')];
const NativeAnnotationTest = bridge.annotation_test;

export const annotationTest = {
  hello(id: number, msg: string): Promise<void> {
    return NativeAnnotationTest.hello(id, msg);
  },

  hello1(id: number): Promise<void> {
    return NativeAnnotationTest.hello1(id);
  },

  hello2(msg: string): Promise<void> {
    return NativeAnnotationTest.hello2(msg);
  },

  hello3(): Promise<void> {
    return NativeAnnotationTest.hello3();
  },

  hello4(): Promise<void> {
    return NativeAnnotationTest.hello4();
  },

  hello5(): Promise<void> {
    return NativeAnnotationTest.hello5();
  },
};