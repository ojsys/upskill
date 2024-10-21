from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Case, When, IntegerField
from .models import Quiz, Question, Answer, QuizAttempt, Course, Lesson, UserProgress, Enrollment



def home(request):
    return render(request, 'home.html')


@login_required
def course_list(request):
    all_courses = Course.objects.all()
    enrolled_courses = Course.objects.filter(enrollment__user=request.user)
    available_courses = all_courses.exclude(id__in=enrolled_courses.values_list('id', flat=True))
    return render(request, 'courses/course_list.html', {
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses
    })

# @login_required
# def enroll_course(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     if request.method == 'POST':
#         Enrollment.objects.get_or_create(user=request.user, course=course)
#         messages.success(request, f"You have successfully enrolled in {course.title}.")
#         return redirect('course_detail', course_id=course.id)
#     return render(request, 'courses/enroll_course.html', {'course': course})

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        if created:
            messages.success(request, f"You have successfully enrolled in {course.title}.")
        else:
            messages.info(request, f"You were already enrolled in {course.title}.")
        return redirect('course_detail', course_id=course.id)
    return render(request, 'courses/enroll_course.html', {'course': course})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    if not is_enrolled:
        return redirect('enroll_course', course_id=course.id)
    
    lessons = course.lessons.order_by('order')
    user_progress = UserProgress.objects.filter(user=request.user, lesson__course=course)
    completed_lessons = user_progress.filter(completed=True).count()
    total_lessons = lessons.count()
    progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'progress_percentage': progress_percentage,
    })


### Lesson Detail

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user_progress, created = UserProgress.objects.get_or_create(user=request.user, lesson=lesson)
    
    if request.method == 'POST':
        if 'complete_lesson' in request.POST:
            user_progress.completed = True
            user_progress.completed_at = timezone.now()
            user_progress.save()
        elif 'upload_file' in request.POST and request.FILES.get('attachment'):
            lesson.attachment = request.FILES['attachment']
            lesson.save()
    
    return render(request, 'courses/lesson_detail.html', {'lesson': lesson, 'user_progress': user_progress})

### User dashboard 

@login_required
def user_dashboard(request):
    enrolled_courses = Course.objects.filter(lessons__userprogress__user=request.user).distinct()
    
    course_progress = enrolled_courses.annotate(
        total_lessons=Count('lessons'),
        completed_lessons=Count(Case(
            When(lessons__userprogress__user=request.user, lessons__userprogress__completed=True, then=1),
            output_field=IntegerField()
        ))
    ).values('id', 'title', 'total_lessons', 'completed_lessons')

    for course in course_progress:
        course['progress_percentage'] = (course['completed_lessons'] / course['total_lessons']) * 100 if course['total_lessons'] > 0 else 0

    return render(request, 'courses/user_dashboard.html', {'course_progress': course_progress})



### Quiz Views

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1
        
        QuizAttempt.objects.create(user=request.user, quiz=quiz, score=score)
        return render(request, 'courses/quiz_results.html', {
            'quiz': quiz,
            'score': score,
            'total_questions': total_questions,
        })

    return render(request, 'courses/take_quiz.html', {'quiz': quiz, 'questions': questions})
