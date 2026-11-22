import React, { useEffect, useRef, useState } from 'react';
import {
  View, Text, Pressable, ActivityIndicator, KeyboardAvoidingView, Platform,
  ScrollView, StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import Field from '../components/Field';
import Banner from '../components/Banner';
import { changePassword } from '../api';
import { colors } from '../theme';

function Rule({ ok, text, style }) {
  return (
    <View style={[styles.rule, style]}>
      <Text style={styles.ruleText}>{text}</Text>
      <Ionicons name={ok ? 'checkmark' : 'close'} size={18} color={ok ? colors.success : colors.error} style={{ marginLeft: 8 }} />
    </View>
  );
}

export default function ChangePasswordScreen({ navigation }) {
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState({ type: '', message: '' });
  const timer = useRef(null);

  useEffect(() => () => clearTimeout(timer.current), []);

  const rules = {
    upper: /[A-Z]/.test(next),
    lower: /[a-z]/.test(next),
    number: /[0-9]/.test(next),
    length: next.length >= 8,
  };
  const allOk = Object.values(rules).every(Boolean);

  const submit = async () => {
    if (!current) return setResult({ type: 'error', message: 'Ingresa tu contraseña actual.' });
    if (!allOk) return setResult({ type: 'error', message: 'La nueva contraseña no cumple los requisitos.' });
    if (next !== confirm) return setResult({ type: 'error', message: 'Las contraseñas nuevas no coinciden.' });

    setLoading(true);
    try {
      const data = await changePassword(current, next, confirm); // PATCH /api/auth/password
      setResult({ type: 'success', message: data.mensaje });
      timer.current = setTimeout(() => navigation.goBack(), 1400);
    } catch (e) {
      setResult({ type: 'error', message: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
          <View style={styles.header}>
            <Pressable hitSlop={12} onPress={() => navigation.goBack()}>
              <Ionicons name="chevron-back" size={26} color="#222" />
            </Pressable>
            <Text style={styles.title}>Cambio de contraseña</Text>
          </View>

          <Text style={styles.subtitle}>Ingresa los datos requeridos</Text>

          <Field label="Contraseña actual" placeholder="Contraseña actual" secure value={current} onChangeText={setCurrent} style={{ marginBottom: 20 }} inputStyle={{ fontSize: 13 }} />
          <Field label="Nueva contraseña" placeholder="Nueva contraseña" secure value={next} onChangeText={setNext} inputStyle={{ fontSize: 13 }} />

          <Text style={styles.hint}>Recuerda que tu contraseña deverá contener los siguientes caracteres</Text>
          <View style={styles.rulesGrid}>
            <Rule ok={rules.upper} text="Mayúsculas" style={{ width: '46%' }} />
            <Rule ok={rules.number} text="Números" style={{ width: '46%' }} />
            <Rule ok={rules.lower} text="Minúsculas" style={{ width: '46%', marginTop: 14 }} />
            <Rule ok={rules.length} text="8 o más caracteres" style={{ width: '54%', marginTop: 14 }} />
          </View>

          <Field label="Vuelve a escribir tu nueva contraseña" placeholder="Nueva contraseña" secure value={confirm} onChangeText={setConfirm} style={{ marginTop: 18 }} inputStyle={{ fontSize: 13 }} />

          <Pressable style={styles.button} onPress={submit} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" size="small" /> : <Text style={styles.buttonText}>cambiar contraseña</Text>}
          </Pressable>
          <Banner type={result.type} message={result.message} />
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.white },
  content: { paddingHorizontal: 26, paddingTop: 20, paddingBottom: 40 },
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 34 },
  title: { marginLeft: 18, fontSize: 20, fontWeight: '600', color: '#222' },
  subtitle: { textAlign: 'center', fontSize: 16, fontWeight: '600', color: '#222', marginBottom: 28 },
  hint: { marginTop: 20, fontSize: 13, color: '#555' },
  rulesGrid: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 14, paddingHorizontal: 4 },
  rule: { flexDirection: 'row', alignItems: 'center' },
  ruleText: { fontSize: 13, color: '#444' },
  button: { alignSelf: 'flex-end', marginTop: 28, backgroundColor: colors.primary, borderRadius: 6, paddingVertical: 8, paddingHorizontal: 14, minWidth: 130, alignItems: 'center' },
  buttonText: { color: '#fff', fontSize: 13, fontWeight: '600' },
});
