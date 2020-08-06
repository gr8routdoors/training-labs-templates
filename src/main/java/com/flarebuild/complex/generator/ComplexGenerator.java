package com.flarebuild.complex.generator;

import org.apache.commons.math3.complex.Complex;


public class ComplexGenerator {
  
  public String generate(final double real, final double imaginary) {
    Complex c = new Complex(real, imaginary);
    return String.format("%.0f+%.0fi", c.getReal(),c.getImaginary());
  }

}
