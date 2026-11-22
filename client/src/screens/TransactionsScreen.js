import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Logo from '../components/Logo';
import { colors } from '../theme';

// Pantalla pendiente de diseño: solo muestra el encabezado.
export default function TransactionsScreen() {
  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={{ padding: 24 }}>
        <Logo />
        <Text style={styles.text}>Transacciones</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.white },
  text: { marginTop: 24, fontSize: 18, color: colors.welcome, fontWeight: '600' },
});
