import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '../theme';

export default function Logo() {
  return (
    <View style={styles.row}>
      <MaterialCommunityIcons name="gavel" size={30} color={colors.primary} />
      <Text style={styles.text}>AbogadosYA</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center' },
  text: { marginLeft: 8, fontSize: 24, color: colors.logo, fontWeight: '500' },
});
