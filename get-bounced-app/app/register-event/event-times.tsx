import { useState } from 'react';
import { Image, StyleSheet, Pressable, View, Button, Platform } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker'; // Import the DateTimePicker

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

import { Link } from 'expo-router';

export default function EventTimes() {
  const [startTime, setStartTime] = useState(new Date()); // State for start time
  const [endTime, setEndTime] = useState(new Date());     // State for end time
  const [showStartTimePicker, setShowStartTimePicker] = useState(false); // Control visibility of start time picker
  const [showEndTimePicker, setShowEndTimePicker] = useState(false);     // Control visibility of end time picker

  const onStartTimeChange = (event: any, selectedDate: any) => {
    const currentDate = selectedDate || startTime;
    setShowStartTimePicker(Platform.OS === 'ios'); // If on iOS, keep showing picker
    setStartTime(currentDate);
  };

  const onEndTimeChange = (event: any, selectedDate: any) => {
    const currentDate = selectedDate || endTime;
    setShowEndTimePicker(Platform.OS === 'ios'); // If on iOS, keep showing picker
    setEndTime(currentDate);
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
        <ThemedText type="subtitle">Input your event start and end times.</ThemedText>

        {/* Start Time Picker */}
        <View style={styles.pickerContainer}>
          <Button title="Select Start Time" onPress={() => setShowStartTimePicker(true)} />
          {showStartTimePicker && (
            <DateTimePicker
              value={startTime}
              mode="time"
              display="default"
              onChange={onStartTimeChange}
            />
          )}
          <ThemedText style={styles.timeText}>Selected Start Time: {startTime.toLocaleTimeString()}</ThemedText>
        </View>

        {/* End Time Picker */}
        <View style={styles.pickerContainer}>
          <Button title="Select End Time" onPress={() => setShowEndTimePicker(true)} />
          {showEndTimePicker && (
            <DateTimePicker
              value={endTime}
              mode="time"
              display="default"
              onChange={onEndTimeChange}
            />
          )}
          <ThemedText style={styles.timeText}>Selected End Time: {endTime.toLocaleTimeString()}</ThemedText>
        </View>

      </ThemedView>
      <Link href="/register-event/event-link" asChild>
        <Pressable style={styles.button}>
          <ThemedText style={styles.text}>Next</ThemedText>
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
