import React, { useState } from 'react';
import {
  View, Text, Pressable, Modal, Animated, LayoutAnimation, Platform, UIManager,
  ActivityIndicator, KeyboardAvoidingView, ScrollView, StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import Logo from '../components/Logo';
import Field from '../components/Field';
import Banner from '../components/Banner';
import { useAuth } from '../context/AuthContext';
import { colors } from '../theme';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

export default function ProfileScreen({ navigation }) {
  const { user, updateUsername, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const [newName, setNewName] = useState('');
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState({ type: '', message: '' });
  const [confirmLogout, setConfirmLogout] = useState(false);

  const toggle = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setOpen((o) => !o);
    setResult({ type: '', message: '' });
  };

  const save = async () => {
    if (!newName.trim()) {
      setResult({ type: 'error', message: 'Introduce un nuevo nombre de usuario.' });
      return;
    }
    setSaving(true);
    try {
      const data = await updateUsername(newName); // PATCH /api/auth/username
      setResult({ type: 'success', message: `${data.mensaje} Nuevo usuario: ${data.username}` });
      setNewName('');
    } catch (e) {
      setResult({ type: 'error', message: e.message });
    } finally {
      setSaving(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
          <Logo />

          <View style={[styles.card, { marginTop: 48 }]}>
            <Text style={styles.label}>Nombre completo</Text>
            <Text style={styles.value}>{user?.nombre_completo}</Text>
          </View>

          <View style={[styles.card, { marginTop: 14 }]}>
            <Pressable style={styles.rowBetween} onPress={toggle}>
              <View>
                <Text style={styles.label}>Nombre de usuario</Text>
                <Text style={styles.value}>{user?.username}</Text>
              </View>
              <Ionicons name={open ? 'chevron-up' : 'chevron-down'} size={22} color="#222" />
            </Pressable>

            {open && (
              <View style={{ marginTop: 14 }}>
                <Field
                  label="Nuevo nombre de usuario"
                  placeholder="Introduce un nuevo nombre de usuario"
                  leftIcon="person-outline"
                  value={newName}
                  onChangeText={setNewName}
                  inputStyle={{ fontSize: 12 }}
                />
                <Pressable style={styles.smallButton} onPress={save} disabled={saving}>
                  {saving ? <ActivityIndicator color="#fff" size="small" /> : <Text style={styles.smallButtonText}>guardar cambios</Text>}
                </Pressable>
                <Banner type={result.type} message={result.message} />
              </View>
            )}
          </View>

          <Pressable style={[styles.card, styles.rowBetween, { marginTop: 14 }]} onPress={() => navigation.navigate('ChangePassword')}>
            <Text style={styles.rowText}>Cambiar contraseña</Text>
            <Ionicons name="chevron-forward" size={22} color="#222" />
          </Pressable>

          <Pressable style={[styles.card, styles.rowBetween, { marginTop: 14 }]} onPress={() => setConfirmLogout(true)}>
            <Text style={styles.rowText}>Cerrar sesión</Text>
            <Ionicons name="chevron-forward" size={22} color="#222" />
          </Pressable>
        </ScrollView>
      </KeyboardAvoidingView>

      <Modal visible={confirmLogout} transparent animationType="fade" onRequestClose={() => setConfirmLogout(false)}>
        <View style={styles.overlay}>
          <View style={styles.dialog}>
            <Text style={styles.dialogTitle}>¿Estás seguro que deseas cerrar sesión?</Text>
            <View style={styles.dialogActions}>
              <Pressable onPress={() => setConfirmLogout(false)}>
                <Text style={styles.dialogAction}>Continuar en AbogadosYA</Text>
              </Pressable>
              <Pressable
                onPress={() => {
                  setConfirmLogout(false);
                  signOut();
                }}
              >
                <Text style={styles.dialogAction}>Cerrar sesión</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.white },
  content: { padding: 24 },
  card: { borderWidth: 1, borderColor: colors.border, borderRadius: 12, paddingVertical: 14, paddingHorizontal: 18, backgroundColor: colors.white },
  rowBetween: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  label: { fontSize: 14, fontWeight: '700', color: colors.label },
  value: { marginTop: 6, fontSize: 14, color: '#333' },
  rowText: { fontSize: 14, fontWeight: '600', color: colors.label },
  smallButton: { alignSelf: 'flex-end', marginTop: 10, backgroundColor: colors.primary, borderRadius: 6, paddingVertical: 7, paddingHorizontal: 12, minWidth: 110, alignItems: 'center' },
  smallButtonText: { color: '#fff', fontSize: 13, fontWeight: '600' },
  overlay: { flex: 1, backgroundColor: colors.overlay, justifyContent: 'center', paddingHorizontal: 24 },
  dialog: { backgroundColor: colors.white, borderWidth: 1, borderColor: colors.border, borderRadius: 14, padding: 18 },
  dialogTitle: { fontSize: 17, color: colors.text, marginBottom: 26 },
  dialogActions: { flexDirection: 'row', justifyContent: 'space-between' },
  dialogAction: { fontSize: 16, color: colors.primary, fontWeight: '500' },
});
