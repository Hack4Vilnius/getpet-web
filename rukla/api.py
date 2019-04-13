from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_tracking.mixins import LoggingMixin

from rukla.models import Answer, GameStatus, Question, Rank, UserInfo


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct', ]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'answers', 'explanation', 'created_at', 'updated_at']


class UserInfoSerializer(serializers.ModelSerializer):
    rank = serializers.StringRelatedField()
    next_rank = serializers.StringRelatedField()

    class Meta:
        model = UserInfo
        fields = ['rank', 'next_rank']


class NewGameSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    user_info = UserInfoSerializer(required=False)

    class Meta:
        model = GameStatus
        fields = ['id', 'game_id', 'questions', 'answered_questions', 'failed_answer', 'user_info', ]


class FinishedGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameStatus
        fields = ['answered_questions', 'failed_answer', 'is_finished']


@method_decorator(name='patch', decorator=swagger_auto_schema(
    operation_description="Submit game results",
))
class FinishGameView(LoggingMixin, UpdateAPIView):
    serializer_class = FinishedGameSerializer
    permission_classes = (IsAuthenticated,)
    queryset = GameStatus.objects.all()
    lookup_field = 'game_id'
    lookup_url_kwarg = 'game_id'

    def perform_update(self, serializer):
        game = serializer.save()

        if game.is_game_won():
            game.user_info.advance_rank()


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="Starts game and updates game status"
))
class NewGameView(LoggingMixin, CreateAPIView):
    serializer_class = NewGameSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        user = self.request.user
        questions = GameStatus.generate_game_questions(user)

        info, _ = UserInfo.objects.get_or_create(
            user=user,
            defaults={
                'rank': Rank.default_rank()
            }
        )

        serializer.save(user_info=info, questions=questions)
