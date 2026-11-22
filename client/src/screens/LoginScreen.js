import React, { useState } from 'react';
import {
  View, Text, Image, Pressable, ActivityIndicator, KeyboardAvoidingView,
  Platform, ScrollView, Linking, StyleSheet, useWindowDimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Logo from '../components/Logo';
import Field from '../components/Field';
import Banner from '../components/Banner';
import { useAuth } from '../context/AuthContext';
import { colors } from '../theme';
import { CONTACT_PHONE, LOCATION_URL } from '../config';

export default function LoginScreen() {
  const { signIn } = useAuth();
  const { height } = useWindowDimensions();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onLogin = async () => {
    if (!username.trim() || !password) {
      setError('Ingresa tu usuario y contraseña.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await signIn(username, password); // al iniciar sesión, la navegación hace la transición a la app
    } catch (e) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.flex} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView
        style={styles.flex}
        contentContainerStyle={{ flexGrow: 1 }}
        keyboardShouldPersistTaps="handled"
        bounces={false}
      >
        <Image
          source={require('../../assets/cochabamba-illustration.jpeg')}
          style={{ width: '100%', height: height * 0.46 }}
          resizeMode="cover"
        />
        <View style={styles.card}>
          <Logo />
          <Text style={styles.welcome}>Te damos la bienvenida</Text>

          <Field
            label="Usuario"
            placeholder="Usuario"
            value={username}
            onChangeText={setUsername}
            decorativeEye
            style={{ marginBottom: 18 }}
          />
          <Field
            label="Contraseña"
            placeholder="Contraseña"
            value={password}
            onChangeText={setPassword}
            secure
            onSubmitEditing={onLogin}
          />

          <Pressable
            style={({ pressed }) => [styles.button, pressed && { opacity: 0.85 }]}
            onPress={onLogin}
            disabled={loading}
          >
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Iniciar sesión</Text>}
          </Pressable>
          <Banner type="error" message={error} />

          <View style={styles.footer}>
            <Pressable style={styles.footerItem} onPress={() => Linking.openURL(CONTACT_PHONE)}>
              <Ionicons name="call-outline" size={30} color={colors.primary} />
              <Text style={styles.footerText}>Contáctanos</Text>
            </Pressable>
            <Pressable style={styles.footerItem} onPress={() => Linking.openURL(LOCATION_URL)}>
              <Ionicons name="location-outline" size={30} color={colors.primary} />
              <Text style={styles.footerText}>Encuéntranos</Text>
            </Pressable>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.white },
  card: {
    flex: 1,
    marginTop: -28,
    backgroundColor: colors.white,
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    paddingHorizontal: 26,
    paddingTop: 22,
    paddingBottom: 24,
  },
  welcome: {
    marginTop: 18,
    marginBottom: 26,
    marginLeft: 2,
    fontSize: 24,
    fontWeight: '700',
    fontStyle: 'italic',
    color: colors.welcome,
  },
  button: {
    marginTop: 26,
    height: 50,
    borderRadius: 6,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: { color: '#fff', fontSize: 20, fontWeight: '500' },
  footer: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 'auto', paddingTop: 24, paddingHorizontal: 4 },
  footerItem: { alignItems: 'center' },
  footerText: { marginTop: 6, fontSize: 15, color: colors.primary, fontWeight: '500' },
});
