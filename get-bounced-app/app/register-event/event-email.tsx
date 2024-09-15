import { Image, StyleSheet, TextInput, Pressable } from 'react-native';

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

import { Link } from 'expo-router';

import { useFormContext } from './eventContext';

export default function EventEmail() {
  const { eventData, updateEventData } = useFormContext()!;

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
        <ThemedText type="subtitle">Email</ThemedText>
        <TextInput
          style={styles.textInput}
          placeholder="Enter email"
          value={eventData.email ?? ''}
          onChangeText={(email) => updateEventData({ email })} // Updates the state when input changes
        />
      </ThemedView>
      <Link href="/register-event/event-name" asChild>
        <Pressable style={styles.button}>
          <ThemedText style={styles.text}>Next</ThemedText>
        </Pressable>
      </Link>
      <Link href="/host" asChild>
        <Pressable style={styles.button}>
          <ThemedText style={styles.text}>Previous</ThemedText>
        </Pressable>
      </Link>
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
  textInput: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    padding: 10,
    borderRadius: 5,
    marginTop: 8,
  },
  button: {
    backgroundColor: "#D0D0D0",
    padding: 10,
    borderRadius: 5,
    margin: 10,
    alignItems: "center",
  },
  text: {
    fontSize: 16,
    fontWeight: "bold",
  }
});