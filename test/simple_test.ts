const bridge = globalThis[Symbol.for('systemservice')];
const NativeSimpleTest = bridge.simple_test;

export interface SimpleTestHello1 {
  id1: number;
  msg1?: string;
}

export interface SimpleTestResponse {
  weather: string; // comment will add to Typescript file
  res: string;
}

export interface SimpleTestHello2Response {
  res1: number;
  res2: string;
}

export interface SimpleTestStatusChange1Data {
  res1: number;
  res2: string;
}

export const simpleTest = {
  hello(msg: string, id?: number): Promise<SimpleTestResponse> {
    return NativeSimpleTest.hello(msg, id);
  },

  hello2(id1: number, msg1?: string): Promise<SimpleTestHello2Response> {
    return NativeSimpleTest.hello2(id1, msg1);
  },

  hello3(id1: number, msg1?: string): Promise<SimpleTestResponse> {
    return NativeSimpleTest.hello3(id1, msg1);
  },

  set statusChange(handler: ((data: SimpleTestResponse) => void) | undefined) {
    NativeSimpleTest.status_change = handler;
  },

  set statusChange1(handler: ((data: SimpleTestStatusChange1Data) => void) | undefined) {
    NativeSimpleTest.status_change1 = handler;
  },
};