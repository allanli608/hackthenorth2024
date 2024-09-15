import { Stack } from 'expo-router/stack';
import { FormProvider } from './guestContext';

export default function Layout() {
    return <FormProvider><Stack screenOptions={{ gestureEnabled: false }} /></FormProvider>;
}