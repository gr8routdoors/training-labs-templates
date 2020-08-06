package com.flarebuild.thirdparty;

import org.apache.commons.math3.complex.Complex;

class math {
  public static void main(final String[] args) {
    Complex complex = new Complex(2.0, 10.0);
    System.out.println("variable complex (" + complex.getClass().toString() + ") = " + complex.toString());
  }
}
