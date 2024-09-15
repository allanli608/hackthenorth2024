import { View, Image, StyleSheet, Pressable, Text } from 'react-native';
import { Link } from 'expo-router';

import * as Clipboard from 'expo-clipboard';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { useState, useEffect } from 'react';
import axiosInstance from '@/axios';

export default function HostHomeScreen() {
  const [myEvents, setMyEvents] = useState([]);

  const copyToClipboard = (eventId: string) => {
    Clipboard.setStringAsync(eventId); // Copy URL to clipboard
    alert("Event code copied to clipboard!");
  };

  useEffect(() => {
    const fetchEvents = async () => {
      const response = await axiosInstance.get('/events', { params: { email: 'L@k' } })
      setMyEvents(response.data);
    }
    fetchEvents();
  }, [])

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#A1CEDC', dark: '#1D3D47' }}
      headerImage={
        <Image
          source={require('@/assets/images/partial-react-logo.png')}
          style={styles.reactLogo}
        />
      }>
      <ThemedText type="title">Create Your Vibe!</ThemedText>
      <Link href="/register-event/event-email" asChild>
        <Pressable style={styles.button}>
          <ThemedText style={styles.text}>Host an Event</ThemedText>
        </Pressable>
      </Link>
      <ThemedText type="subtitle">My Events</ThemedText>
      {myEvents.map((event: any) => {
        return (
          <View key={event[0]} style={{ display: 'flex', flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <ThemedText >{event[3]}</ThemedText>
            <ThemedText >{event[5]}</ThemedText>
            <ThemedText >{(new Date(event[4].split('T')[0])).toDateString()}</ThemedText>
            <Pressable style={styles.smallButton} onPress={async () => {
              console.log(event[2])
              const response = await axiosInstance.get(`/event/${event[2]}/guests`)
              console.log(response.data);
              const guests = response.data.map((guest: any) => guest[2]);
              alert('Your guests are:\n' + guests.join(', '));
            }}
            ><Text>Guests</Text></Pressable>
            <Pressable style={{ ...styles.smallButton, backgroundColor: '#faa4a4' }} onPress={() => {
              copyToClipboard(event[2]);
            }}><Text>Code</Text></Pressable>
          </View>
        )
      })}
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
  smallButton: {
    backgroundColor: "#86aeb4",
    padding: 2,
    borderRadius: 3,
    alignItems: "center",
  }
});
