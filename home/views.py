from django.shortcuts import render, redirect, get_list_or_404
from conseil_communautaire.models import ConseilVille
from contact.forms import ContactForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from contact.models import ContactEmail
from services.models import Service


def is_staff_or_superuser(user):
    """Vérifier si l'utilisateur est staff ou superuser.

    Args:
        user: L'utilisateur à vérifier.

    Returns:
        bool: True si l'utilisateur est staff ou superuser.
    """
    return user.is_staff or user.is_superuser


def home(request):
    # Donnée requises pour la page d'accueil
    if Service.objects.exists():
        services = get_list_or_404(Service.objects.order_by('title'))
    else:
        services = None

    if ConseilVille.objects.exists():
        communes = get_list_or_404(ConseilVille)
        nb_communes = len(communes)
        nb_habitants = 0
        for commune in communes:
            nb_habitants += commune.nb_habitants

    else:
        communes = None
        nb_communes = None
        nb_habitants = None

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            # Ne pas envoyer le mail si aucun destinataire n'est défini
            if ContactEmail.objects.exists():
                ccsa_contact = ContactEmail.objects.filter(is_active=True).values_list(
                    "email", flat=True)

                context = {
                    'first_name': contact_form.cleaned_data['first_name'],
                    'last_name': contact_form.cleaned_data['last_name'],
                    'email': contact_form.cleaned_data['email'],
                    'phone': contact_form.cleaned_data['phone'],
                    'message': contact_form.cleaned_data['message'],
                }

                # Mail au CCSA
                text_content = render_to_string("email_text.txt", context)
                html_content = render_to_string("email_html.html", context)
                from_email = contact_form.cleaned_data['email']
                to_email = ccsa_contact  # Replace with your email address
                msg = EmailMultiAlternatives(
                    subject=f"CONTACT - CCSA : \
                        {contact_form.cleaned_data['first_name']} \
                            {contact_form.cleaned_data['last_name']}",
                    body=text_content,
                    from_email=from_email,
                    to=to_email
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # mail de confirmation au client
                text_content_client = render_to_string("email_text_client.txt", context)
                html_content_client = render_to_string("email_html_client.html",
                                                       context)
                from_email = ccsa_contact[0]
                to_email_client = [contact_form.cleaned_data['email']]
                msg_client = EmailMultiAlternatives(
                    subject=f"CONFIRMATION DE CONTACT - CCSA : \
                        {contact_form.cleaned_data['first_name']} \
                            {contact_form.cleaned_data['last_name']}",
                    body=text_content_client,
                    from_email=from_email,
                    to=to_email_client
                )

                msg_client.attach_alternative(html_content_client, "text/html")
                msg_client.send()

                return redirect('home')
            else:
                print("Aucun contact CCSA défini")
                return redirect('home')
        else:
            print(contact_form.errors)
            return redirect('home')
    else:
        contact_form = ContactForm()

    context = {
        'services': services,
        'communes': communes,
        'contact_form': contact_form,
        'nb_communes': nb_communes,
        'nb_habitants': nb_habitants,
    }

    return render(request, 'home/index.html', context)


def conseil(request):
    return render(request, 'home/conseil.html')


def presentation(request):

    if ConseilVille.objects.exists():
        communes = get_list_or_404(ConseilVille)
        nb_communes = len(communes)
        nb_habitants = 0
        for commune in communes:
            nb_habitants += commune.nb_habitants
    else:
        communes = None
        nb_communes = 0
        nb_habitants = 0

    context = {
        'communes': communes,
        'nb_communes': nb_communes,
        'nb_habitants': nb_habitants,
    }

    return render(request, 'home/presentation.html', context)


def marches_publics(request):
    return render(request, 'home/marches-publics.html')


def mobilite(request):
    return render(request, 'home/mobilite.html')


def habitat(request):
    return render(request, 'home/habitat.html')


def collecte_dechets(request):
    return render(request, 'home/collecte-dechets.html')


def encombrants(request):
    return render(request, 'home/encombrants.html')


def dechetteries(request):
    return render(request, 'home/dechetteries.html')


def maisons_sante(request):
    return render(request, 'home/maisons-sante.html')


def mutuelle(request):
    return render(request, 'home/mutuelle.html')


def plui(request):
    return render(request, 'home/plui.html')


def projet_plui(request):
    return render(request, 'home/projet-plui.html')


def equipe(request):
    return render(request, 'home/equipe.html')


def mentions_legales(request):
    return render(request, 'home/mentions-legales.html')


def politique_confidentialite(request):
    return render(request, 'home/politique-confidentialite.html')


def cookies(request):
    return render(request, 'home/cookies.html')


def plan_du_site(request):
    return render(request, 'home/plan-du-site.html')


def accessibilite(request):
    return render(request, 'home/accessibilite.html')


def custom_handler404(request, exception=None):
    """Vue personnalisée pour la page 404."""
    response = render(request, '404.html', status=404)
    return response
