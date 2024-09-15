import { createContext, useContext, useState, ReactNode } from 'react';

type GuestData = {
    eventId?: string,
    guestName?: string,
    guestEmail?: string,
};

type GuestContextType = {
    guestData: GuestData;
    updateGuestData: (newData: Partial<GuestData>) => void;
};

const FormContext = createContext<GuestContextType | undefined>(undefined);

export const useFormContext = (): GuestContextType => {
    const context = useContext(FormContext)
    if (!context) {
        throw new Error('useFormContext must be used within a FormProvider');
    }
    return context;
};

export const FormProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [guestData, setGuestData] = useState<GuestData>({});

    const updateGuestData = (newData: Partial<GuestData>) => {
        setGuestData((prevData) => ({ ...prevData, ...newData }));
    };

    return (
        <FormContext.Provider value={{ guestData, updateGuestData }}>
            {children}
        </FormContext.Provider >
    );
};
