import { useState } from 'react';
import { Image, StyleSheet, Pressable, View, Button, Platform } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker'; // Import the DateTimePicker

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

import { Link } from 'expo-router';
import { useFormContext } from './eventContext';
import { useRouter } from 'expo-router';

export default function EventDate() {
  const { eventData, updateEventData } = useFormContext();
  const router = useRouter();

  const [date, setDate] = useState(new Date()); // State for date
  const [showDatePicker, setShowDateTimePicker] = useState(false); // Control visibility of start date time picker

  const onDateChange = (event: any, selectedDate: any) => {
    const currentDate = selectedDate || date;
    setShowDateTimePicker(Platform.OS === 'ios'); // If on iOS, keep showing picker
    setDate(currentDate);
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
        <ThemedText type="subtitle">Input your Event Date</ThemedText>

        {/* Start Time Picker */}
        <View style={styles.pickerContainer}>
          <Button title="Select Date" onPress={() => setShowDateTimePicker(true)} />
          {showDatePicker && (
            <DateTimePicker
              value={date}
              mode="date"
              display="default"
              onChange={onDateChange}
            />
          )}
          <ThemedText style={styles.timeText}>Selected Date: {date.toLocaleDateString()}</ThemedText>
        </View>
      </ThemedView>
      <Link href="/register-event/event-times" asChild>
        <Pressable style={styles.button} onPress={() => {
          updateEventData({
            eventDate: date.toISOString().split('T')[0],
          });
        }}>
          <ThemedText style={styles.text}>Next</ThemedText>
        </Pressable>
      </Link>
      <Link href="/register-event/event-location" asChild>
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
    marginVertical: 8,
  },
  text: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  button: {
    backgroundColor: '#D0D0D0',
    padding: 10,
    borderRadius: 5,
    margin: 10,
    alignItems: 'center',
  },
  pickerContainer: {
    marginVertical: 10,
  },
  timeText: {
    marginTop: 8,
    fontSize: 16,
  },
});
