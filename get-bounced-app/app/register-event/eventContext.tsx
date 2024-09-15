import { createContext, useContext, useState } from 'react';

type EventData = {
    eventName: string;
    eventDate: string;
    eventLocation: string;
    eventStartTime: string;
    eventEndTime: string;
    // eventId: string;
};

const FormContext = createContext<{ formData: EventData; updateFormData: (newData: Partial<EventData>) => void } | null>(null);

export const useFormContext = () => useContext(FormContext);

export const FormProvider = ({ children }: { children: React.ReactElement }) => {
    const [formData, setFormData] = useState({
        eventName: '',
        eventDate: '',
        eventLocation: '',
        eventStartTime: '',
        eventEndTime: '',
    });

    const updateFormData = (newData: Partial<EventData>) => {
        setFormData((prevData) => ({ ...prevData, ...newData }));
    };

    return (
        <FormContext.Provider value={{ formData, updateFormData }}>
            {children}
        </FormContext.Provider >
    );
};
