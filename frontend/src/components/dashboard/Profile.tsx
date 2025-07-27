import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { 
  User,
  Phone,
  CreditCard,
  Mail,
  Edit3,
  Save,
  X,
  Shield,
  CheckCircle
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

interface ProfileProps {
  onClose: () => void;
}

interface UserProfile {
  name: string;
  mobile: string;
  email: string;
  accountName: string;
  accountNumber: string;
  accountType: string;
  status: 'active' | 'pending' | 'suspended';
  memberSince: string;
}

const Profile = ({ onClose }: ProfileProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState<UserProfile>({
    name: "Rahul Sharma",
    mobile: "+91 98765 43210",
    email: "rahul.sharma@email.com",
    accountName: "Rahul Sharma",
    accountNumber: "FI1234567890",
    accountType: "Premium",
    status: "active",
    memberSince: "March 2023"
  });

  const [editedProfile, setEditedProfile] = useState<UserProfile>(profile);

  const handleEdit = () => {
    setEditedProfile(profile);
    setIsEditing(true);
  };

  const handleSave = () => {
    setProfile(editedProfile);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedProfile(profile);
    setIsEditing(false);
  };

  const handleInputChange = (field: keyof UserProfile, value: string) => {
    setEditedProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success/10 text-success border-success';
      case 'pending':
        return 'bg-warning/10 text-warning border-warning';
      case 'suspended':
        return 'bg-destructive/10 text-destructive border-destructive';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="w-full max-w-4xl bg-background rounded-2xl border shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Sidebar Layout */}
          <div className="flex h-[500px]">
            {/* Left Sidebar - Profile Overview */}
            <div className="w-1/3 bg-gradient-to-b from-primary/10 to-primary/5 border-r border-border p-4">
              {/* Profile Avatar & Status */}
              <div className="text-center mb-4">
                <div className="relative inline-block">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary/80 rounded-full flex items-center justify-center mb-2">
                    <User className="w-8 h-8 text-white" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-success rounded-full border-2 border-background flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                  </div>
                </div>
                <h2 className="text-lg font-bold">{profile.name}</h2>
                <p className="text-xs text-muted-foreground">{profile.email}</p>
                <Badge className="mt-1 bg-success/20 text-success border-success/30 text-xs">
                  {profile.status.charAt(0).toUpperCase() + profile.status.slice(1)}
                </Badge>
              </div>

              {/* Quick Stats */}
              <div className="space-y-2 mb-4">
                <div className="bg-background/50 rounded-lg p-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Account Type</span>
                    <span className="font-semibold text-xs">{profile.accountType}</span>
                  </div>
                </div>
                <div className="bg-background/50 rounded-lg p-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Member Since</span>
                    <span className="font-semibold text-xs">{profile.memberSince}</span>
                  </div>
                </div>
                <div className="bg-background/50 rounded-lg p-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Account Number</span>
                    <span className="font-semibold text-xs font-mono">{profile.accountNumber}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2">
                {!isEditing ? (
                  <Button
                    variant="default"
                    size="sm"
                    onClick={handleEdit}
                    className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-xs"
                  >
                    <Edit3 className="w-3 h-3 mr-1" />
                    Edit Profile
                  </Button>
                ) : (
                  <div className="space-y-2">
                    <Button
                      variant="default"
                      size="sm"
                      onClick={handleSave}
                      className="w-full bg-gradient-to-r from-success to-success/80 hover:from-success/90 hover:to-success/70 text-xs"
                    >
                      <Save className="w-3 h-3 mr-1" />
                      Save Changes
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCancel}
                      className="w-full text-xs"
                    >
                      Cancel
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {/* Right Content Area */}
            <div className="flex-1 p-4 overflow-y-auto">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-xl font-bold">Profile Settings</h1>
                  <p className="text-xs text-muted-foreground">Manage your account information and preferences</p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="h-6 w-6"
                >
                  <X className="w-3 h-3" />
                </Button>
              </div>

              {/* Content Tabs */}
              <div className="space-y-4">
                {/* Personal Information Section */}
                <div className="bg-card border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 bg-primary/10 rounded-lg">
                      <User className="w-4 h-4 text-primary" />
                    </div>
                    <h3 className="text-base font-semibold">Personal Information</h3>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label htmlFor="name" className="text-xs font-medium">Full Name</Label>
                      {isEditing ? (
                        <Input
                          id="name"
                          value={editedProfile.name}
                          onChange={(e) => handleInputChange('name', e.target.value)}
                          placeholder="Enter your full name"
                          className="h-8 text-sm"
                        />
                      ) : (
                        <div className="h-8 px-2 py-1 bg-muted rounded-md flex items-center">
                          <span className="font-medium text-sm">{profile.name}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="space-y-1">
                      <Label htmlFor="mobile" className="text-xs font-medium">Mobile Number</Label>
                      {isEditing ? (
                        <Input
                          id="mobile"
                          value={editedProfile.mobile}
                          onChange={(e) => handleInputChange('mobile', e.target.value)}
                          placeholder="Enter mobile number"
                          className="h-8 text-sm"
                        />
                      ) : (
                        <div className="h-8 px-2 py-1 bg-muted rounded-md flex items-center">
                          <span className="font-medium text-sm">{profile.mobile}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="space-y-1 md:col-span-2">
                      <Label htmlFor="email" className="text-xs font-medium">Email Address</Label>
                      {isEditing ? (
                        <Input
                          id="email"
                          type="email"
                          value={editedProfile.email}
                          onChange={(e) => handleInputChange('email', e.target.value)}
                          placeholder="Enter email address"
                          className="h-8 text-sm"
                        />
                      ) : (
                        <div className="h-8 px-2 py-1 bg-muted rounded-md flex items-center">
                          <span className="font-medium text-sm">{profile.email}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Account Information Section */}
                <div className="bg-card border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 bg-info/10 rounded-lg">
                      <CreditCard className="w-4 h-4 text-info" />
                    </div>
                    <h3 className="text-base font-semibold">Account Information</h3>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label htmlFor="accountName" className="text-xs font-medium">Account Name</Label>
                      {isEditing ? (
                        <Input
                          id="accountName"
                          value={editedProfile.accountName}
                          onChange={(e) => handleInputChange('accountName', e.target.value)}
                          placeholder="Enter account name"
                          className="h-8 text-sm"
                        />
                      ) : (
                        <div className="h-8 px-2 py-1 bg-muted rounded-md flex items-center">
                          <span className="font-medium text-sm">{profile.accountName}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="space-y-1">
                      <Label htmlFor="accountNumber" className="text-xs font-medium">Account Number</Label>
                      {isEditing ? (
                        <Input
                          id="accountNumber"
                          value={editedProfile.accountNumber}
                          onChange={(e) => handleInputChange('accountNumber', e.target.value)}
                          placeholder="Enter account number"
                          className="h-8 text-sm"
                        />
                      ) : (
                        <div className="h-8 px-2 py-1 bg-muted rounded-md flex items-center justify-between">
                          <span className="font-medium text-sm font-mono">{profile.accountNumber}</span>
                          <div className="flex items-center gap-1">
                            <CheckCircle className="w-3 h-3 text-success" />
                            <span className="text-xs text-success">Verified</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Security Information */}
                {!isEditing && (
                  <div className="bg-card border rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="p-1.5 bg-warning/10 rounded-lg">
                        <Shield className="w-4 h-4 text-warning" />
                      </div>
                      <h3 className="text-base font-semibold">Security Information</h3>
                    </div>
                    
                    <div className="bg-muted/50 rounded-lg p-3">
                      <p className="text-xs text-muted-foreground">
                        Your account information is encrypted and secure. For any changes to sensitive information, 
                        please contact our support team.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default Profile; 