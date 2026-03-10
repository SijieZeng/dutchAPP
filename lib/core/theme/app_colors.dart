import 'package:flutter/material.dart';

class AppColors {
  // Brand
  static const orange = Color(0xFFFF6B2C); // Dutch orange
  static const orangeLight = Color(0xFFFF8F5C);
  static const orangeDark = Color(0xFFE55A1B);

  // UI
  static const background = Color(0xFF1A1A2E);
  static const surface = Color(0xFF16213E);
  static const surfaceLight = Color(0xFF0F3460);
  static const cardWhite = Color(0x33FFFFFF); // 20% white
  static const cardWhiteHover = Color(0x4DFFFFFF); // 30% white

  // Text
  static const textPrimary = Color(0xFFFFFFFF);
  static const textSecondary = Color(0xB3FFFFFF); // 70% white
  static const textHint = Color(0x80FFFFFF); // 50% white

  // Feedback
  static const correct = Color(0xFF4CAF50);
  static const incorrect = Color(0xFFEF5350);
  static const correctLight = Color(0x334CAF50);
  static const incorrectLight = Color(0x33EF5350);

  // Gradient overlay for background image
  static const backgroundGradient = [
    Color(0x00000000),
    Color(0x80000000),
  ];
}
