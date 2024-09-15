import { Image, StyleSheet, Pressable } from 'react-native';
import * as Clipboard from 'expo-clipboard'; // Import Clipboard API

import { Link } from 'expo-router';
import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { useFormContext } from './eventContext';

export default function EventLink() {
  const { eventData } = useFormContext();

  const copyToClipboard = () => {
    Clipboard.setStringAsync(eventData.eventId ?? ''); // Copy URL to clipboard
    alert("Event code copied to clipboard!");
  };

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#A1CEDC', dark: '#1D3D47' }}
      headerImage={
        <Image
          source={require('@/assets/images/partial-react-logo.png')}
          style={styles.reactLogo}
        />
      }>
      <ThemedView style={styles.titleContainer}>
        <ThemedText type="title">You're All Set!</ThemedText>
        <HelloWave />
      </ThemedView>
      <ThemedView style={styles.stepContainer}>
        <ThemedText type="default">
          Send this code to your guests for them to register:
        </ThemedText>
        <ThemedText type="subtitle">
          {eventData.eventId}
        </ThemedText>
        <Pressable style={styles.button} onPress={copyToClipboard}>
          <ThemedText style={styles.text}>Copy Event Code</ThemedText>
        </Pressable>
        <Pressable style={styles.button}>
          <Link style={styles.link} href="/">
            <ThemedText style={styles.buttonText}>Return to Home</ThemedText>
          </Link>
        </Pressable>
      </ThemedView>
    </ParallaxScrollView>
  );
}

const styles = StyleSheet.create({
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  stepContainer: {
    gap: 8,
    marginBottom: 8,
  },
  reactLogo: {
    height: 178,
    width: 290,
    bottom: 0,
    left: 0,
    position: 'absolute',
  },
  button: {
    backgroundColor: '#D0D0D0',
    padding: 10,
    borderRadius: 5,
    margin: 10,
    alignItems: 'center',
  },
  text: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: "bold",
    textAlign: "center",
  },
  link: {
    width: '100%'
  }
});
