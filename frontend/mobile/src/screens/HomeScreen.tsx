import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { apiBaseUrl } from '../config/api';

type NextStep = 'login' | 'dashboard';

export function HomeScreen() {
  const [nextStep, setNextStep] = useState<NextStep>('login');

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>ASSET-GUDANG · MOBILE</Text>
        <Text accessibilityRole="header" style={styles.title}>Aset tertata, kerja lebih mudah.</Text>
        <Text style={styles.description}>Fondasi aplikasi gudang sudah siap. Kelola aset dari genggaman pada tahap berikutnya.</Text>
        <View style={styles.card}>
          <Text style={styles.badge}>FASE 1 · FONDASI EXPO</Text>
          <Text style={styles.heading}>Selamat datang</Text>
          <Text style={styles.body}>Ini adalah layar awal React Native, bukan data inventaris langsung. Login dan dashboard belum terhubung.</Text>
          <Text style={styles.label}>Konfigurasi API</Text>
          <Text selectable style={styles.body}>{apiBaseUrl ?? 'Belum diatur — mode fondasi tanpa koneksi backend.'}</Text>
          <Text style={styles.note}>URL terisi bukan berarti server sudah terhubung. Layar ini tidak mengirim permintaan API.</Text>
        </View>
        <Text accessibilityRole="header" style={styles.heading}>Langkah berikutnya</Text>
        <View style={styles.actions}>
          <Pressable accessibilityRole="button" accessibilityState={{ selected: nextStep === 'login' }} onPress={() => setNextStep('login')} style={[styles.button, nextStep === 'login' && styles.selected]}>
            <Text style={[styles.buttonText, nextStep === 'login' && styles.selectedText]}>Rencana login</Text>
          </Pressable>
          <Pressable accessibilityRole="button" accessibilityState={{ selected: nextStep === 'dashboard' }} onPress={() => setNextStep('dashboard')} style={[styles.button, nextStep === 'dashboard' && styles.selected]}>
            <Text style={[styles.buttonText, nextStep === 'dashboard' && styles.selectedText]}>Rencana dashboard</Text>
          </Pressable>
        </View>
        <View style={styles.card} accessibilityLiveRegion="polite">
          <Text style={styles.heading}>{nextStep === 'login' ? '01 · Login' : '02 · Dashboard'}</Text>
          <Text style={styles.body}>{nextStep === 'login'
            ? 'Berikutnya: formulir masuk, validasi, autentikasi backend, dan penyimpanan sesi yang aman.'
            : 'Berikutnya: ringkasan aset, daftar inventaris, pencarian, dan status gudang dari API.'}</Text>
          <Text style={styles.note}>Belum tersedia pada fase ini.</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#f3f6fb' },
  content: { padding: 24, gap: 20, maxWidth: 640, width: '100%', alignSelf: 'center' },
  eyebrow: { color: '#215c49', fontSize: 12, fontWeight: '700', letterSpacing: 1.5 },
  title: { color: '#152a25', fontSize: 32, lineHeight: 40, fontWeight: '800' },
  description: { color: '#53645e', fontSize: 16, lineHeight: 25 },
  card: { padding: 22, backgroundColor: '#fff', borderRadius: 20, gap: 12, borderWidth: 1, borderColor: '#dce5e0' },
  badge: { color: '#215c49', fontSize: 11, fontWeight: '700', letterSpacing: 1 },
  heading: { color: '#152a25', fontSize: 20, fontWeight: '700' },
  body: { color: '#40554b', fontSize: 15, lineHeight: 24 },
  label: { color: '#152a25', fontSize: 14, fontWeight: '700', marginTop: 6 },
  note: { color: '#66766e', fontSize: 13, lineHeight: 20 },
  actions: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  button: { minHeight: 48, paddingVertical: 14, paddingHorizontal: 18, borderRadius: 12, backgroundColor: '#e2ebe6' },
  selected: { backgroundColor: '#215c49' },
  buttonText: { color: '#215c49', fontWeight: '700', fontSize: 14 },
  selectedText: { color: '#fff' },
});
