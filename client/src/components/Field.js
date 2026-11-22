import React, { useState } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme';

/**
 * Campo de texto con el estilo de las pantallas.
 * - secure: muestra el ojo para ver/ocultar el texto.
 * - decorativeEye: dibuja el ojo sin acción (como en el campo "Usuario" del diseño).
 * - leftIcon: icono a la izquierda (ej. persona).
 */
export default function Field({
  label,
  secure,
  decorativeEye,
  leftIcon,
  style,
  inputStyle,
  ...props
}) {
  const [hidden, setHidden] = useState(true);
  return (
    <View style={style}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <View style={styles.box}>
        {leftIcon ? (
          <Ionicons name={leftIcon} size={20} color={colors.inactive} style={{ marginRight: 8 }} />
        ) : null}
        <TextInput
          style={[styles.input, inputStyle]}
          placeholderTextColor={colors.placeholder}
          secureTextEntry={secure ? hidden : false}
          autoCapitalize="none"
          autoCorrect={false}
          {...props}
        />
        {secure ? (
          <Pressable hitSlop={10} onPress={() => setHidden((h) => !h)}>
            <Ionicons name={hidden ? 'eye' : 'eye-off'} size={22} color="#555" />
          </Pressable>
        ) : null}
        {decorativeEye ? <Ionicons name="eye" size={22} color="#555" /> : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  label: { fontSize: 14, fontWeight: '700', color: colors.label, marginBottom: 8 },
  box: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.inputBg,
    borderRadius: 12,
    paddingHorizontal: 14,
    height: 46,
  },
  input: { flex: 1, fontSize: 14, color: colors.text, height: '100%' },
});
