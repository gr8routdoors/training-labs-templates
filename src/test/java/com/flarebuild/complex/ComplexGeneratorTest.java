package com.flarebuild.complex;

import org.junit.Test;

import static org.junit.Assert.*;
import com.flarebuild.complex.generator.*;

public class ComplexGeneratorTest {

  @Test
  public void testGenerator() {
      ComplexGenerator generator = new ComplexGenerator();
      assertEquals("Complex number pretty pring", "2+3i", generator.generate(2.0,3.0));
  }
}
