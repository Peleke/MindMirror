import {
    Avatar,
    AvatarBadge,
    AvatarFallbackText,
    AvatarImage
} from "@/components/ui/avatar";
import { Box } from "@/components/ui/box";
import { Button, ButtonIcon, ButtonText } from "@/components/ui/button";
import { Center } from "@/components/ui/center";
import {
    FormControl,
    FormControlError,
    FormControlErrorIcon,
    FormControlErrorText,
    FormControlLabel,
    FormControlLabelText,
} from "@/components/ui/form-control";
import { Heading } from "@/components/ui/heading";
import { HStack } from "@/components/ui/hstack";
import {
    AlertCircleIcon,
    ChevronDownIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    CloseIcon,
    EditIcon,
    Icon,
    MenuIcon,
    SettingsIcon
} from "@/components/ui/icon";
import { Input, InputField } from "@/components/ui/input";
import {
    Modal,
    ModalBackdrop,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalHeader,
} from "@/components/ui/modal";
import { Pressable } from "@/components/ui/pressable";
import { SafeAreaView } from "@/components/ui/safe-area-view";
import { ScrollView } from "@/components/ui/scroll-view";
import {
    Select,
    SelectBackdrop,
    SelectContent,
    SelectDragIndicator,
    SelectDragIndicatorWrapper,
    SelectIcon,
    SelectInput,
    SelectItem,
    SelectPortal,
    SelectTrigger,
} from "@/components/ui/select";
import { Text } from "@/components/ui/text";
import { Toast, ToastTitle, useToast } from "@/components/ui/toast";
import { VStack } from "@/components/ui/vstack";
import { useAuth } from '@/features/auth/context/AuthContext';
import { UPDATE_USER_METADATA } from '../../src/services/api/mutations';
import { LIST_TRADITIONS } from '../../src/services/api/queries';
import { useMutation, useQuery } from '@apollo/client';
import { cn } from "@gluestack-ui/nativewind-utils/cn";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigation } from '@react-navigation/native';
import { AlertCircle, type LucideIcon } from "lucide-react-native";
import React, { useRef, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Keyboard, Platform } from "react-native";
import { z } from "zod";

// Placeholder icons - you can replace these with actual icons
const ProfileIcon = () => <Icon as={SettingsIcon} />;
const SubscriptionIcon = () => <Icon as={SettingsIcon} />;
const DownloadIcon = () => <Icon as={SettingsIcon} />;
const FaqIcon = () => <Icon as={SettingsIcon} />;
const NewsBlogIcon = () => <Icon as={SettingsIcon} />;
const HomeIcon = () => <Icon as={SettingsIcon} />;
const GlobeIcon = () => <Icon as={SettingsIcon} />;
const InboxIcon = () => <Icon as={SettingsIcon} />;
const HeartIcon = () => <Icon as={SettingsIcon} />;
const CameraSparklesIcon = () => <Icon as={SettingsIcon} />;
const EditPhotoIcon = () => <Icon as={EditIcon} />;

type Icons = {
  iconName: LucideIcon | typeof Icon;
  iconText: string;
};

const SettingsList: Icons[] = [
  {
    iconName: ProfileIcon,
    iconText: "Profile",
  },
  {
    iconName: SettingsIcon,
    iconText: "Preferences",
  },
  {
    iconName: SubscriptionIcon,
    iconText: "Subscription",
  },
];

const ResourcesList: Icons[] = [
  {
    iconName: DownloadIcon,
    iconText: "Downloads",
  },
  {
    iconName: FaqIcon,
    iconText: "FAQs",
  },
  {
    iconName: NewsBlogIcon,
    iconText: "News & Blogs",
  },
];

type BottomTabs = {
  iconName: LucideIcon | typeof Icon;
  iconText: string;
};

const bottomTabsList: BottomTabs[] = [
  {
    iconName: HomeIcon,
    iconText: "Home",
  },
  {
    iconName: GlobeIcon,
    iconText: "Community",
  },
  {
    iconName: InboxIcon,
    iconText: "Inbox",
  },
  {
    iconName: HeartIcon,
    iconText: "Favourite",
  },
  {
    iconName: ProfileIcon,
    iconText: "Profile",
  },
];

interface UserStats {
  friends: string;
  friendsText: string;
  followers: string;
  followersText: string;
  rewards: string;
  rewardsText: string;
  posts: string;
  postsText: string;
}

const userData: UserStats[] = [
  {
    friends: "45K",
    friendsText: "Friends",
    followers: "500M",
    followersText: "Followers",
    rewards: "40",
    rewardsText: "Rewards",
    posts: "346",
    postsText: "Posts",
  },
];

const Sidebar = () => {
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [selectedIndexResources, setSelectedIndexResources] = useState<number>(0);
  
  const handlePress = (index: number) => {
    setSelectedIndex(index);
  };
  
  const handlePressResources = (index: number) => {
    setSelectedIndexResources(index);
  };
  
  return (
    <ScrollView className="h-full" contentContainerStyle={{ flexGrow: 1 }}>
      <VStack
        className="h-full flex-1 w-[280px] py-4 pr-4 pl-8 items-center border-r border-border-300"
        space="xl"
      >
        <VStack className="w-full px-2 pt-3 pb-4" space="xs">
          <Text className="text-typography-600 px-4 py-2">SETTINGS</Text>
          {SettingsList.map((item, index) => {
            return (
              <Pressable
                onPress={() => handlePress(index)}
                key={index}
                className={`flex-row px-4 py-3 items-center gap-2 rounded
              ${
                index === selectedIndex
                  ? "bg-background-950 "
                  : "bg-background-0"
              }
              `}
              >
                <Icon
                  as={item.iconName}
                  className={`
              ${
                index === selectedIndex
                  ? "stroke-background-0 fill-background-800"
                  : "stroke-background-800 fill-none"
              }
              `}
                />
                <Text
                  className={`
              ${
                index === selectedIndex
                  ? "text-typography-0"
                  : "text-typography-700"
              }
              `}
                >
                  {item.iconText}
                </Text>
              </Pressable>
            );
          })}
        </VStack>
        <VStack className="w-full px-2 pt-3 pb-4" space="xs">
          <Text className="text-typography-600 px-4 py-2">RESOURCES</Text>
          {ResourcesList.map((item, index) => {
            return (
              <Pressable
                onPress={() => handlePressResources(index)}
                key={index}
                className={`flex-row px-4 py-3 items-center gap-2 rounded
              ${
                index === selectedIndexResources
                  ? "bg-background-950 "
                  : "bg-background-0"
              }
              `}
              >
                <Icon
                  as={item.iconName}
                  className={`
              ${
                index === selectedIndexResources
                  ? "stroke-background-0"
                  : "stroke-background-800"
              }
              h-10 w-10
              `}
                />
                <Text
                  className={`
              ${
                index === selectedIndexResources
                  ? "text-typography-0"
                  : "text-typography-700"
              }
              `}
                >
                  {item.iconText}
                </Text>
              </Pressable>
            );
          })}
        </VStack>
      </VStack>
    </ScrollView>
  );
};

const DashboardLayout = (props: any) => {
  return (
    <VStack className="h-full w-full bg-background-0">
      <Box className="md:hidden">
        <MobileHeader title={props.title} />
      </Box>
      <Box className="hidden md:flex">
        <WebHeader title={props.title} />
      </Box>
      <VStack className="h-full w-full">
        <VStack className="w-full flex-1">{props.children}</VStack>
      </VStack>
    </VStack>
  );
};

function MobileFooter({ footerIcons }: { footerIcons: any }) {
  return (
    <HStack
      className={cn(
        "bg-background-0 justify-between w-full absolute left-0 bottom-0 right-0 p-3 overflow-hidden items-center border-t-border-300 md:hidden border-t",
        { "pb-5": Platform.OS === "ios" },
        { "pb-5": Platform.OS === "android" }
      )}
    >
      {footerIcons.map(
        (
          item: { iconText: string; iconName: any },
          index: React.Key | null | undefined
        ) => {
          return (
            <Pressable
              className="px-0.5 flex-1 flex-col items-center"
              key={index}
            >
              <Icon
                as={item.iconName}
                size="md"
                className="h-[32px] w-[65px]"
              />
              <Text className="text-xs text-center text-typography-600">
                {item.iconText}
              </Text>
            </Pressable>
          );
        }
      )}
    </HStack>
  );
}

function WebHeader(props: { title: string }) {
  const navigation = useNavigation();
  
  return (
    <HStack className="pt-4 pr-10 pb-3 bg-background-0 items-center justify-between border-b border-border-300">
      <HStack className="items-center">
        <Pressable
          onPress={() => {
            navigation.goBack();
          }}
        >
          <Icon as={ChevronLeftIcon} size="lg" className="mx-5" />
        </Pressable>
        <Text className="text-2xl">{props.title}</Text>
      </HStack>

      <Avatar className="h-9 w-9">
        <AvatarBadge />
      </Avatar>
    </HStack>
  );
}

function MobileHeader(props: { title: string }) {
  const navigation = useNavigation();
  
  return (
    <HStack
      className="py-6 px-4 border-b border-border-300 bg-background-0 items-center justify-between"
      space="md"
    >
      <HStack className="items-center" space="sm">
        <Pressable
          onPress={() => {
            navigation.goBack();
          }}
        >
          <Icon as={ChevronLeftIcon} />
        </Pressable>
        <Text className="text-xl">{props.title}</Text>
      </HStack>
      <Box className="h-8 w-20" />
    </HStack>
  );
}

type userSchemaDetails = z.infer<typeof userSchema>;

// Define the Zod schema
const userSchema = z.object({
  firstName: z
    .string()
    .min(1, "First name is required")
    .max(50, "First name must be less than 50 characters"),
  lastName: z
    .string()
    .min(1, "Last name is required")
    .max(50, "Last name must be less than 50 characters"),
  gender: z.enum(["male", "female", "other"]),
  phoneNumber: z
    .string()
    .regex(
      /^\+?[1-9]\d{1,14}$/,
      "Phone number must be a valid international phone number"
    ),
  city: z
    .string()
    .min(1, "City is required")
    .max(100, "City must be less than 100 characters"),
  state: z
    .string()
    .min(1, "State is required")
    .max(100, "State must be less than 100 characters"),
  country: z
    .string()
    .min(1, "Country is required")
    .max(100, "Country must be less than 100 characters"),
  zipcode: z
    .string()
    .min(1, "Zipcode is required")
    .max(20, "Zipcode must be less than 20 characters"),
});

interface AccountCardType {
  iconName: LucideIcon | typeof Icon;
  subText: string;
  endIcon: LucideIcon | typeof Icon;
}

const accountData: AccountCardType[] = [
  {
    iconName: InboxIcon,
    subText: "Settings",
    endIcon: ChevronRightIcon,
  },
];

const MainContent = () => {
  const [showModal, setShowModal] = useState(false);
  const [selectedTradition, setSelectedTradition] = useState('canon-default');
  const { user, signOut } = useAuth();
  const toast = useToast();
  
  const {
    control,
    formState: { errors },
  } = useForm({
    defaultValues: {
      tradition: 'canon-default'
    }
  });

  // Fetch available traditions
  const { data: traditionsData, loading: traditionsLoading, error: traditionsError } = useQuery(LIST_TRADITIONS);

  // Get current tradition from user metadata
  React.useEffect(() => {
    const currentTradition = user?.user_metadata?.journal_preferences?.tradition || 'canon-default';
    setSelectedTradition(currentTradition);
  }, [user]);

  // Update user metadata mutation
  const [updateUserMetadata, { loading: updateLoading }] = useMutation(UPDATE_USER_METADATA, {
    onCompleted: (data) => {
      toast.show({
        title: "Success",
        description: "Tradition preference updated successfully.",
      });
    },
    onError: (error) => {
      console.error('Update metadata error:', error);
      toast.show({
        title: "Feature Not Available",
        description: "Tradition preference saving is not yet implemented. Your selection will be remembered for this session.",
        action: "warning",
      });
    }
  });

  const handleTraditionChange = (tradition: string) => {
    setSelectedTradition(tradition);
    
    // Update user metadata with new tradition preference
    const currentMetadata = user?.user_metadata || {};
    const updatedMetadata = {
      ...currentMetadata,
      journal_preferences: {
        ...currentMetadata.journal_preferences,
        tradition: tradition
      }
    };

    updateUserMetadata({
      variables: {
        metadata: updatedMetadata
      }
    });
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      toast.show({
        title: "Signed out",
        description: "You have been successfully signed out.",
      });
    } catch (error) {
      toast.show({
        title: "Error",
        description: "Failed to sign out. Please try again.",
        action: "error",
      });
    }
  };

  return (
    <VStack className="h-full w-full">
      <ModalComponent showModal={showModal} setShowModal={setShowModal} />
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          flexGrow: 1,
        }}
        className="flex-1"
      >
        <VStack className="w-full pb-4" space="2xl">
          <Box className="relative w-full h-[300px] bg-primary-600">
            {/* Placeholder for banner image */}
            <Box className="w-full h-full bg-gradient-to-b from-primary-600 to-primary-800" />
          </Box>
          <HStack className="absolute pt-6 px-10 hidden md:flex">
            <Text className="text-typography-900 font-roboto">
              home &gt; {` `}
            </Text>
            <Text className="font-semibold text-typography-900 ">profile</Text>
          </HStack>
          <Center className="absolute mt-6 w-full pt-6 pb-4">
            <VStack space="lg" className="items-center">
              <Avatar size="2xl" className="bg-primary-600">
                <AvatarFallbackText>
                  {user?.user_metadata?.full_name || user?.email || "User"}
                </AvatarFallbackText>
                <AvatarImage
                  alt="Profile Image"
                  height={"100%"}
                  width={"100%"}
                  source={{ uri: "https://i.pravatar.cc/300" }}
                />
                <AvatarBadge />
              </Avatar>
              <VStack className="gap-1 w-full items-center">
                <Text size="2xl" className="font-roboto text-white">
                  {user?.user_metadata?.full_name || user?.email || "User"}
                </Text>
                <Text className="font-roboto text-sm text-white opacity-80">
                  United States
                </Text>
              </VStack>
              <Button
                variant="outline"
                action="secondary"
                onPress={() => setShowModal(true)}
                className="gap-3 relative bg-white"
              >
                <ButtonText className="text-dark">Edit Profile</ButtonText>
                <ButtonIcon as={EditIcon} />
              </Button>
            </VStack>
          </Center>
          <VStack className="mx-6" space="lg">
            <Heading className="font-roboto" size="xl">
              Account
            </Heading>
            <VStack space="sm">
              <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                Journal Tradition
              </Text>
              <Text className="text-xs text-typography-500 dark:text-gray-400">
                Determines the set of texts from which the AI derives knowledge and advice for your journaling experience.
              </Text>
              <Controller
                name="tradition"
                control={control}
                defaultValue={selectedTradition}
                render={({ field: { onChange, value } }) => (
                  <Select 
                    onValueChange={(newValue) => {
                      onChange(newValue);
                      handleTraditionChange(newValue);
                    }} 
                    selectedValue={value}
                  >
                    <SelectTrigger variant="outline" size="md">
                      <SelectInput placeholder="Select tradition" />
                      <SelectIcon className="mr-3" as={ChevronDownIcon} />
                    </SelectTrigger>
                    <SelectPortal>
                      <SelectBackdrop />
                      <SelectContent>
                        <SelectDragIndicatorWrapper>
                          <SelectDragIndicator />
                        </SelectDragIndicatorWrapper>
                        {traditionsLoading ? (
                          <SelectItem label="Loading..." value="" />
                        ) : traditionsError ? (
                          <SelectItem label="Error loading traditions" value="" />
                        ) : traditionsData?.listTraditions ? (
                          traditionsData.listTraditions.map((tradition: string) => (
                            <SelectItem 
                              key={tradition} 
                              label={tradition} 
                              value={tradition} 
                            />
                          ))
                        ) : (
                          <SelectItem label="canon-default" value="canon-default" />
                        )}
                      </SelectContent>
                    </SelectPortal>
                  </Select>
                )}
              />
              {updateLoading && (
                <Text className="text-xs text-gray-500 text-center">
                  Updating preference...
                </Text>
              )}
            </VStack>
            
            <Button
              variant="outline"
              action="negative"
              onPress={handleSignOut}
              className="gap-3"
            >
              <ButtonText className="text-red-600">Sign Out</ButtonText>
            </Button>
          </VStack>
        </VStack>
      </ScrollView>
    </VStack>
  );
};

const ModalComponent = ({
  showModal,
  setShowModal,
}: {
  showModal: boolean;
  setShowModal: any;
}) => {
  const ref = useRef(null);
  const {
    control,
    formState: { errors },
    handleSubmit,
    reset,
  } = useForm<userSchemaDetails>({
    resolver: zodResolver(userSchema),
  });

  const handleKeyPress = () => {
    Keyboard.dismiss();
  };
  const [isEmailFocused, setIsEmailFocused] = useState(false);
  const [isNameFocused, setIsNameFocused] = useState(false);
  const onSubmit = (_data: userSchemaDetails) => {
    setShowModal(false);
    reset();
  };

  return (
    <Modal
      isOpen={showModal}
      onClose={() => {
        setShowModal(false);
      }}
      finalFocusRef={ref}
      size="lg"
    >
      <ModalBackdrop />
      <ModalContent>
        <Box className={"w-full h-[215px] "}>
          <Box className="w-full h-full bg-gradient-to-b from-primary-600 to-primary-800" />
        </Box>
        <Pressable className="absolute bg-background-500 rounded-full items-center justify-center h-8 w-8 right-6 top-44">
          <Icon as={CameraSparklesIcon} />
        </Pressable>
        <ModalHeader className="absolute w-full">
          <Heading size="2xl" className="text-typography-800 pt-4 pl-4">
            Edit Profile
          </Heading>
          <ModalCloseButton>
            <Icon
              as={CloseIcon}
              size="md"
              className="stroke-background-400 group-[:hover]/modal-close-button:stroke-background-700 group-[:active]/modal-close-button:stroke-background-900 group-[:focus-visible]/modal-close-button:stroke-background-900"
            />
          </ModalCloseButton>
        </ModalHeader>
        <Center className="w-full absolute top-16">
          <Avatar size="2xl">
            <AvatarImage
              source={{ uri: "https://via.placeholder.com/150" }}
            />
            <AvatarBadge className="justify-center items-center bg-background-500">
              <Icon as={EditPhotoIcon} />
            </AvatarBadge>
          </Avatar>
        </Center>
        <ModalBody className="px-10 py-6">
          <VStack space="2xl">
            <HStack className="items-center justify-between">
              <FormControl
                isInvalid={!!errors.firstName || isNameFocused}
                className="w-[47%]"
              >
                <FormControlLabel className="mb-2">
                  <FormControlLabelText>First Name</FormControlLabelText>
                </FormControlLabel>
                <Controller
                  name="firstName"
                  control={control}
                  rules={{
                    validate: async (value) => {
                      try {
                        await userSchema.parseAsync({
                          firstName: value,
                        });
                        return true;
                      } catch (error: any) {
                        return error.message;
                      }
                    },
                  }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <Input>
                      <InputField
                        placeholder="First Name"
                        type="text"
                        value={value}
                        onChangeText={onChange}
                        onBlur={onBlur}
                        onSubmitEditing={handleKeyPress}
                        returnKeyType="done"
                      />
                    </Input>
                  )}
                />
                <FormControlError>
                  <FormControlErrorIcon as={AlertCircleIcon} size="md" />
                  <FormControlErrorText>
                    {errors?.firstName?.message}
                  </FormControlErrorText>
                </FormControlError>
              </FormControl>
              <FormControl
                isInvalid={!!errors.lastName || isNameFocused}
                className="w-[47%]"
              >
                <FormControlLabel className="mb-2">
                  <FormControlLabelText>Last Name</FormControlLabelText>
                </FormControlLabel>
                <Controller
                  name="lastName"
                  control={control}
                  rules={{
                    validate: async (value) => {
                      try {
                        await userSchema.parseAsync({
                          lastName: value,
                        });
                        return true;
                      } catch (error: any) {
                        return error.message;
                      }
                    },
                  }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <Input>
                      <InputField
                        placeholder="Last Name"
                        type="text"
                        value={value}
                        onChangeText={onChange}
                        onBlur={onBlur}
                        onSubmitEditing={handleKeyPress}
                        returnKeyType="done"
                      />
                    </Input>
                  )}
                />
                <FormControlError>
                  <FormControlErrorIcon as={AlertCircleIcon} size="md" />
                  <FormControlErrorText>
                    {errors?.lastName?.message}
                  </FormControlErrorText>
                </FormControlError>
              </FormControl>
            </HStack>
            <HStack className="items-center justify-between">
              <FormControl className="w-[47%]" isInvalid={!!errors.gender}>
                <FormControlLabel className="mb-2">
                  <FormControlLabelText>Gender</FormControlLabelText>
                </FormControlLabel>
                <Controller
                  name="gender"
                  control={control}
                  rules={{
                    validate: async (value) => {
                      try {
                        await userSchema.parseAsync({ city: value });
                        return true;
                      } catch (error: any) {
                        return error.message;
                      }
                    },
                  }}
                  render={({ field: { onChange, value } }) => (
                    <Select onValueChange={onChange} selectedValue={value}>
                      <SelectTrigger variant="outline" size="md">
                        <SelectInput placeholder="Select" />
                        <SelectIcon className="mr-3" as={ChevronDownIcon} />
                      </SelectTrigger>
                      <SelectPortal>
                        <SelectBackdrop />
                        <SelectContent>
                          <SelectDragIndicatorWrapper>
                            <SelectDragIndicator />
                          </SelectDragIndicatorWrapper>
                          <SelectItem label="Male" value="male" />
                          <SelectItem label="Female" value="female" />
                          <SelectItem label="Others" value="others" />
                        </SelectContent>
                      </SelectPortal>
                    </Select>
                  )}
                />
                <FormControlError>
                  <FormControlErrorIcon as={AlertCircle} size="md" />
                  <FormControlErrorText>
                    {errors?.gender?.message}
                  </FormControlErrorText>
                </FormControlError>
              </FormControl>

              <FormControl className="w-[47%]" isInvalid={!!errors.phoneNumber}>
                <FormControlLabel className="mb-2">
                  <FormControlLabelText>Phone number</FormControlLabelText>
                </FormControlLabel>
                <Controller
                  name="phoneNumber"
                  control={control}
                  rules={{
                    validate: async (value) => {
                      try {
                        await userSchema.parseAsync({ phoneNumber: value });
                        return true;
                      } catch (error: any) {
                        return error.message;
                      }
                    },
                  }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <HStack className="gap-1">
                      <Select className="w-[28%]">
                        <SelectTrigger variant="outline" size="md">
                          <SelectInput placeholder="+91" />
                          <SelectIcon className="mr-1" as={ChevronDownIcon} />
                        </SelectTrigger>
                        <SelectPortal>
                          <SelectBackdrop />
                          <SelectContent>
                            <SelectDragIndicatorWrapper>
                              <SelectDragIndicator />
                            </SelectDragIndicatorWrapper>
                            <SelectItem label="93" value="93" />
                            <SelectItem label="155" value="155" />
                            <SelectItem label="1-684" value="-1684" />
                          </SelectContent>
                        </SelectPortal>
                      </Select>
                      <Input className="flex-1">
                        <InputField
                          placeholder="89867292632"
                          type="text"
                          value={value}
                          onChangeText={onChange}
                          keyboardType="number-pad"
                          onBlur={onBlur}
                          onSubmitEditing={handleKeyPress}
                          returnKeyType="done"
                        />
                      </Input>
                    </HStack>
                  )}
                />
                <FormControlError>
                  <FormControlErrorIcon as={AlertCircle} size="md" />
                  <FormControlErrorText>
                    {errors?.phoneNumber?.message}
                  </FormControlErrorText>
                </FormControlError>
              </FormControl>
            </HStack>
            <HStack className="items-center justify-between">
              <FormControl
                className="w-[47%]"
                isInvalid={(!!errors.city || isEmailFocused) && !!errors.city}
              >
                <FormControlLabel className="mb-2">
                  <FormControlLabelText>City</FormControlLabelText>
                </FormControlLabel>
                <Controller
                  name="city"
                  control={control}
                  rules={{
                    validate: async (value) => {
                      try {
                        await userSchema.parseAsync({ city: value });
                        return true;
                      } catch (error: any) {
                        return error.message;
                      }
                    },
                  }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <Select onValueChange={onChange} selectedValue={value}>
                      <SelectTrigger variant="outline" size="md">
                        <SelectInput placeholder="Select" />
                        <SelectIcon className="mr-3" as={ChevronDownIcon} />
                      </SelectTrigger>
                      <SelectPortal>
                        <SelectBackdrop />
                        <SelectContent>
                          <SelectDragIndicatorWrapper>
                            <SelectDragIndicator />
                          </SelectDragIndicatorWrapper>
                          <SelectItem label="Bengaluru" value="Bengaluru" />
                          <SelectItem label="Udupi" value="Udupi" />
                          <SelectItem label="Others" value="Others" />
                        </SelectContent>
                      </SelectPortal>
                    </Select>
                  )}
                />
                <FormControlError>
                  <FormControlErrorIcon as={AlertCircle} size="md" />
                  <FormControlErrorText>
                    {errors?.city?.message}
                  </FormControlErrorText>
                </FormControlError>
              </FormControl>

              <FormControl
                className="w-[47%]"
                isInvalid={(!!errors.state || isEmailFocused) && !!errors.state}
              >
                <FormControlLabel className="mb-2">
                  <FormControlLabelText>State</FormControlLabelText>
                </FormControlLabel>
                <Controller
                  name="state"
                  control={control}
                  rules={{
                    validate: async (value) => {
                      try {
                        await userSchema.parseAsync({ state: value });
                        return true;
                      } catch (error: any) {
                        return error.message;
                      }
                    },
                  }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <Select onValueChange={onChange} selectedValue={value}>
                      <SelectTrigger variant="outline" size="md">
                        <SelectInput placeholder="Select" />
                        <SelectIcon className="mr-3" as={ChevronDownIcon} />
                      </SelectTrigger>
                      <SelectPortal>
                        <SelectBackdrop />
                        <SelectContent>
                          <SelectDragIndicatorWrapper>
                            <SelectDragIndicator />
                          </SelectDragIndicatorWrapper>
                          <SelectItem label="Karnataka" value="Karnataka" />
                          <SelectItem label="Haryana" value="Haryana" />
                          <SelectItem label="Others" value="Others" />
                        </SelectContent>
                      </SelectPortal>
                    </Select>
                  )}
                />
                <FormControlError>
                  <FormControlErrorIcon as={AlertCircle} size="md" />
                  <FormControlErrorText>
                    {errors?.state?.message}
                  </FormControlErrorText>
                </FormControlError>
              </FormControl>
            </HStack>
            <HStack className="items-center justify-between">
              <FormControl
                className="w-[47%]"
                isInvalid={
                  (!!errors.country || isEmailFocused) && !!errors.country
                }
              >
                <FormControlLabel className="mb-2">
                  <FormControlLabelText>Country</FormControlLabelText>
                </FormControlLabel>
                <Controller
                  name="country"
                  control={control}
                  rules={{
                    validate: async (value) => {
                      try {
                        await userSchema.parseAsync({ country: value });
                        return true;
                      } catch (error: any) {
                        return error.message;
                      }
                    },
                  }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <Select onValueChange={onChange} selectedValue={value}>
                      <SelectTrigger variant="outline" size="md">
                        <SelectInput placeholder="Select" />
                        <SelectIcon className="mr-3" as={ChevronDownIcon} />
                      </SelectTrigger>
                      <SelectPortal>
                        <SelectBackdrop />
                        <SelectContent>
                          <SelectDragIndicatorWrapper>
                            <SelectDragIndicator />
                          </SelectDragIndicatorWrapper>
                          <SelectItem label="India" value="India" />
                          <SelectItem label="Sri Lanka" value="Sri Lanka" />
                          <SelectItem label="Others" value="Others" />
                        </SelectContent>
                      </SelectPortal>
                    </Select>
                  )}
                />
                <FormControlError>
                  <FormControlErrorIcon as={AlertCircle} size="md" />
                  <FormControlErrorText>
                    {errors?.country?.message}
                  </FormControlErrorText>
                </FormControlError>
              </FormControl>
              <FormControl
                className="w-[47%]"
                isInvalid={!!errors.zipcode || isEmailFocused}
              >
                <FormControlLabel className="mb-2">
                  <FormControlLabelText>Zipcode</FormControlLabelText>
                </FormControlLabel>
                <Controller
                  name="zipcode"
                  control={control}
                  rules={{
                    validate: async (value) => {
                      try {
                        await userSchema.parseAsync({
                          zipCode: value,
                        });
                        return true;
                      } catch (error: any) {
                        return error.message;
                      }
                    },
                  }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <Input>
                      <InputField
                        placeholder="Enter 6 - digit zip code"
                        type="text"
                        value={value}
                        onChangeText={onChange}
                        onBlur={onBlur}
                        onSubmitEditing={handleKeyPress}
                        returnKeyType="done"
                      />
                    </Input>
                  )}
                />
                <FormControlError>
                  <FormControlErrorIcon as={AlertCircle} size="md" />
                  <FormControlErrorText>
                    {errors?.zipcode?.message}
                  </FormControlErrorText>
                </FormControlError>
              </FormControl>
            </HStack>
            <Button
              onPress={() => {
                handleSubmit(onSubmit)();
              }}
              className="flex-1 p-2"
            >
              <ButtonText>Save Changes</ButtonText>
            </Button>
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default function ProfileScreen() {
  return (
    <SafeAreaView className="h-full w-full">
      <DashboardLayout title="MindMirror">
        <MainContent />
      </DashboardLayout>
    </SafeAreaView>
  );
} 