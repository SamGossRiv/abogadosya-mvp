import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, ScrollView, Pressable, ActivityIndicator, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Logo from '../components/Logo';
import Banner from '../components/Banner';
import { useAuth } from '../context/AuthContext';
import { getMe } from '../api';
import { colors } from '../theme';

const pretty = (o) => JSON.stringify(o, null, 2);

export default function HomeScreen() {
  const { session, user } = useAuth();
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadMe = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      setMe(await getMe()); // GET /api/auth/me
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMe();
  }, [loadMe, user?.username]);

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <Logo />
        <Text style={styles.hello}>Hola, {user?.nombre_completo}</Text>

        <Text style={styles.title}>POST /auth/login</Text>
        <View style={styles.card}>
          <Text style={styles.code}>{pretty(session)}</Text>
        </View>

        <Text style={styles.title}>GET /auth/me</Text>
        <View style={styles.card}>
          {loading ? <ActivityIndicator color={colors.primary} /> : <Text style={styles.code}>{me ? pretty(me) : '—'}</Text>}
        </View>
        <Banner type="error" message={error} />

        <Pressable style={styles.button} onPress={loadMe}>
          <Text style={styles.buttonText}>volver a consultar</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.white },
  content: { padding: 24, paddingBottom: 40 },
  hello: { marginTop: 24, fontSize: 20, fontWeight: '700', fontStyle: 'italic', color: colors.welcome },
  title: { marginTop: 22, marginBottom: 8, fontSize: 14, fontWeight: '700', color: colors.label },
  card: { borderWidth: 1, borderColor: colors.border, borderRadius: 12, padding: 14 },
  code: { fontSize: 12, color: colors.text, fontFamily: undefined },
  button: { marginTop: 20, alignSelf: 'flex-end', backgroundColor: colors.primary, borderRadius: 6, paddingVertical: 8, paddingHorizontal: 14 },
  buttonText: { color: '#fff', fontSize: 13, fontWeight: '600' },
});
