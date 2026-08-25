from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Lead, Comment, Task, Activity, Profile


class ProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'user_name', 'user_email', 'organization', 'timezone', 'reminder_days']
        read_only_fields = ['user']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author', read_only=True)
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'lead', 'lead_name', 'body', 'author', 'author_name', 'kind', 'created_at']
        read_only_fields = ['created_at']


class TaskSerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    lead_status = serializers.CharField(source='lead.status', read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'lead', 'lead_name', 'lead_status', 'title', 'completed', 'created_at']
        read_only_fields = ['created_at']


class ActivitySerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.name', read_only=True)
    
    class Meta:
        model = Activity
        fields = ['id', 'lead', 'lead_name', 'action', 'details', 'created_by', 'created_at']
        read_only_fields = ['created_at']


class LeadSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    comments_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'company', 'email', 'phone', 'source', 'status', 'status_display',
            'last_contacted', 'next_follow_up', 'budget', 'notes', 'owner', 'owner_name', 
            'owner_email', 'created_at', 'updated_at', 'comments_count', 'tasks_count', 
            'completed_tasks_count'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    def get_completed_tasks_count(self, obj):
        return obj.tasks.filter(completed=True).count()


class LeadDetailSerializer(LeadSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    
    class Meta(LeadSerializer.Meta):
        fields = LeadSerializer.Meta.fields + ['comments', 'tasks', 'activities']


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'company', 'email', 'phone', 'source', 'status', 
            'last_contacted', 'next_follow_up', 'budget', 'notes'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class LeadStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['status']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title']

    def create(self, validated_data):
        lead_id = self.context['lead_id']
        validated_data['lead_id'] = lead_id
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['body', 'kind', 'author']

    def create(self, validated_data):
        lead_id = self.context['lead_id']
        validated_data['lead_id'] = lead_id
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
