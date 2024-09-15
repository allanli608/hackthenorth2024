import React, { useState } from 'react';
import { Platform, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { ResizeMode, Video } from 'expo-av';

import { Image, StyleSheet, Pressable } from 'react-native';

import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

import { Link, useLocalSearchParams, useRouter } from 'expo-router';
import DemoVideo from '@/assets/videos/DemoVideo.mp4';
import axiosInstance from '@/axios';
import { useFormContext } from './guestContext';

export default function RegisterGuestFace() {
  const router = useRouter();

  const [loading, setLoading] = useState(false);

  const { eventId } = useLocalSearchParams();
  const { guestData } = useFormContext()!;
  const [video, setVideo] = useState<string | null>(null);

  const requestPermissions = async (): Promise<boolean> => {
    const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
    return cameraStatus === 'granted';
  };

  const recordVideo = async (): Promise<void> => {
    const hasPermission = await requestPermissions();

    if (!hasPermission) {
      alert('Camera and audio permissions are required to record a video.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      cameraType: ImagePicker.CameraType.front,
      allowsEditing: true,
      quality: 1,
      videoMaxDuration: 12,  // Max duration of 12 seconds
    });

    if (!result.canceled) {
      console.log('MIME Type:', result.assets[0].mimeType);
      setVideo(result.assets[0].uri);  // Use `result.assets[0].uri` to get the video URI
    }
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append('guestData', JSON.stringify(guestData));

    if (!video) {
      console.error('No video recorded');
      return;
    }

    const extension = Platform.OS === 'android' ? 'mp4' : 'mov';
    const fileName = `${guestData.guestName}_video.${extension}`;

    formData.append('guestVideo', {
      uri: video,
      type: `video/${extension}`,
      name: fileName,
    } as any);

    try {
      const response = await axiosInstance.post(`/register-guest/${eventId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      })
      console.log('Upload successful:', response.data);
    } catch (error) {
      console.error(error)
    }

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
      </ThemedView>
      <ThemedView style={styles.stepContainer}>
        <ThemedText type="subtitle">Please record a ~10s video of your face including tilts to the <ThemedText style={{ fontWeight: '700' }}>left, right, up, and down</ThemedText>.</ThemedText>
        <View style={styles.centeredView}>
          <ThemedText type="default">Example:</ThemedText>
          <Video
            source={DemoVideo}
            rate={1.0}
            volume={1.0}
            isMuted={true}  // Mute video during playback
            isLooping={true}
            resizeMode={ResizeMode.COVER}
            shouldPlay
            style={{ width: 300, height: 300 }} />
        </View>
        <Pressable style={styles.record} onPress={recordVideo}>
          <ThemedText style={styles.buttonText}>{video ? "Re-record Video" : "Record Video"}</ThemedText>
        </Pressable>
        <View style={styles.centeredView}>
          {video && (
            <Video
              source={{ uri: video! }}
              rate={1.0}
              volume={1.0}
              isMuted={true}  // Mute video during playback
              isLooping={true}
              resizeMode={ResizeMode.COVER}
              shouldPlay
              style={{ width: 300, height: 300 }}
            />
          )}
        </View>
      </ThemedView>
      <Pressable style={styles.button} onPress={async () => {
        setLoading(true);
        await handleSubmit();
        setLoading(false);
        router.push('/register-guest/guest-confirm');
      }}>
        <ThemedText style={styles.buttonText}>{loading ? 'Loading' : 'Next'}</ThemedText>
      </Pressable>
      <Pressable style={styles.button}>
        <Link style={styles.link} href="/register-guest/guest-email">
          <ThemedText style={styles.buttonText}>Previous</ThemedText>
        </Link>
      </Pressable>
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
  record: {
    backgroundColor: "#22c9f8",
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
  },
  centeredView: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  }
});