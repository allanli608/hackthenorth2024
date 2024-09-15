import { Image, StyleSheet, Pressable } from 'react-native';
import * as Clipboard from 'expo-clipboard'; // Import Clipboard API

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

export default function EventLink() {
  const eventUrl = "https://forms.gle/RBhfGhYCC6uYSbVz8"; // Your event URL

  const copyToClipboard = () => {
    Clipboard.setStringAsync(eventUrl); // Copy URL to clipboard
    alert("Event link copied to clipboard!");
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
        <ThemedText type="title">Register For an Event</ThemedText>
        <HelloWave />
      </ThemedView>
      <ThemedView style={styles.stepContainer}>
        <ThemedText type="subtitle">
          This is your event link. Send this to your guests for them to register!
        </ThemedText>
        <Pressable style={styles.button} onPress={copyToClipboard}>
          <ThemedText style={styles.text}>Copy Event Link</ThemedText>
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
});
