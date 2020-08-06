
package com.flarebuild.message;

import message_object.MessageObjectOuterClass.MessageObject;

public class Main {
  public static void main(String[] args)  {
    System.out.println(makeMessage(0.5f, "50 cents"));
  }

  public static MessageObject makeMessage(Float value, String message) {
    MessageObject.Builder m = MessageObject.newBuilder();
    m.setValue(value);
    m.setMessage(message);
    return m.build();
  }
}