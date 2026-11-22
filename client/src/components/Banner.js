import React, { useEffect, useRef } from 'react';
import { Animated, Text, StyleSheet } from 'react-native';
import { colors } from '../theme';

/** Muestra el resultado de una llamada a la API con una transición suave. */
export default function Banner({ type, message }) {
  const anim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    anim.setValue(0);
    if (message) {
      Animated.timing(anim, { toValue: 1, duration: 280, useNativeDriver: true }).start();
    }
  }, [message, type]);

  if (!message) return null;
  const color = type === 'error' ? colors.error : colors.success;
  return (
    <Animated.View
      style={[
        styles.box,
        {
          borderColor: color,
          opacity: anim,
          transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [-8, 0] }) }],
        },
      ]}
    >
      <Text style={[styles.text, { color }]}>{message}</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  box: { borderWidth: 1, borderRadius: 10, paddingVertical: 8, paddingHorizontal: 12, marginTop: 12 },
  text: { fontSize: 13, fontWeight: '600' },
});
