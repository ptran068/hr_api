from rest_framework import serializers

from api_user.models.banks import Banks
from api_user.models.user_banks import UserBanks
from api_user.models.user_identity import UserIdentity
from api_user.models.user_contact import UserContact
from api_user.models.user_education import UserEducation
from api_user.models.user_family_members import UserFamilyMembers
from api_user.models.user_insurance import UserInsurance


class BanksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banks
        fields = '__all__'

    def create(self, validate_data):
        return Banks.objects.create(**validate_data)


class UserBanksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBanks
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False}
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # get bank name
        bank = Banks.objects.filter(id=ret.get('bank')).first()
        if bank:
            ret.update(bank_name=bank.name)
        return ret

    def create(self, validated_data):
        return UserBanks.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.account_number = validated_data.get('account_number', instance.account_number)
        instance.bank = validated_data.get('bank', instance.bank)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.save()
        return instance


class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContact
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False}
        }

    def create(self, validated_data):
        return UserContact.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.permanent_address = validated_data.get('permanent_address', instance.permanent_address)
        instance.temporary_address = validated_data.get('temporary_address', instance.temporary_address)
        instance.household_registration_number = validated_data.get('household_registration_number',
                                                                    instance.household_registration_number)
        instance.contact_emergency = validated_data.get('contact_emergency', instance.contact_emergency)
        instance.save()
        return instance


class UserEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEducation
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False}
        }

    def create(self, validated_data):
        return UserEducation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.school = validated_data.get('school', instance.school)
        instance.degree = validated_data.get('degree', instance.degree)
        instance.graduated_year = validated_data.get('graduated_year', instance.graduated_year)
        instance.field_of_study = validated_data.get('field_of_study', instance.field_of_study)
        instance.additional_notes = validated_data.get('additional_notes', instance.additional_notes)
        instance.save()
        return instance


class UserIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserIdentity
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False}
        }

    def create(self, validated_data):
        return UserIdentity.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.identity_number = validated_data.get('identity_number', instance.identity_number)
        instance.issue_date = validated_data.get('issue_date', instance.issue_date)
        instance.issue_place = validated_data.get('issue_place', instance.issue_place)
        instance.place_of_birth = validated_data.get('place_of_birth', instance.place_of_birth)
        instance.save()
        return instance


class UserFamilyMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFamilyMembers
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False}
        }

    def create(self, validated_data):
        return UserFamilyMembers.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.relationship = validated_data.get('relationship', instance.relationship)
        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get("request")
        access_user = request.user
        if not (access_user.is_staff or access_user.id == instance.user.id):
            return None
        else:
            return ret


class UserInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInsurance
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False}
        }

    def create(self, validated_data):
        return UserInsurance.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.social_insurance_code = validated_data.get('social_insurance_code', instance.social_insurance_code)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.save()
        return instance
