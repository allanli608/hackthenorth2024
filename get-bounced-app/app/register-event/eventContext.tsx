import { createContext, useContext, useState, ReactNode } from 'react';

type EventData = {
    eventName?: string;
    eventDate?: string;
    eventLocation?: string;
    eventStartTime?: string;
    eventEndTime?: string;
    eventId?: string;
    email?: string;
};

type EventContextType = {
    eventData: EventData;
    updateEventData: (newData: Partial<EventData>) => void;
};

const FormContext = createContext<EventContextType | undefined>(undefined);

export const useFormContext = (): EventContextType => {
    const context = useContext(FormContext);
    if (!context) {
        throw new Error('useFormContext must be used within a FormProvider');
    }
    return context;
}

export const FormProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [eventData, setEventData] = useState<EventData>({});

    const updateEventData = (newData: Partial<EventData>) => {
        setEventData((prevData) => ({ ...prevData, ...newData }));
    };

    return (
        <FormContext.Provider value={{ eventData, updateEventData }}>
            {children}
        </FormContext.Provider >
    );
};
