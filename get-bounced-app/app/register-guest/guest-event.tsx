import { Image, StyleSheet, Pressable, TextInput } from 'react-native';

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

import { Link, useRouter } from 'expo-router';
import { useFormContext } from './guestContext';
import axiosInstance from '@/axios';

export default function RegisterGuestEvent() {
  const router = useRouter();
  const { guestData, updateGuestData } = useFormContext();

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
        <ThemedText type="subtitle">Event Code</ThemedText>
        <ThemedText type="default">Ask your host for the event code!</ThemedText>
        <TextInput
          style={styles.textInput}
          placeholder="word-word-word-word"
          value={guestData.eventId ?? ''}
          onChangeText={eventId => updateGuestData({ eventId })} // Updates the state when input changes
        />
      </ThemedView>
      <Pressable style={styles.button} onPress={async () => {
        const response = await axiosInstance.get(`/event/${guestData.eventId}`);
        console.log('test', response.data);
        if (response.data) {
          router.push('/register-guest/guest-name');
        }
        else {
          alert('Invalid event code');
        }
      }}>
        <ThemedText style={styles.buttonText}>Next</ThemedText>
      </Pressable>
      <Pressable style={styles.button}>
        <Link style={styles.link} href="/">
          <ThemedText style={styles.buttonText}>Previous</ThemedText>
        </Link>
      </Pressable>
    </ParallaxScrollView >
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
