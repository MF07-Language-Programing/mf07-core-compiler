#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[50];
} Animal;

typedef struct {
    Animal base;
    char secret[50];
} Dog;

const char* Dog_species = "Canis familiaris";

Dog* Dog_new(const char* name) {
    Dog* d = (Dog*)malloc(sizeof(Dog));
    if (!d) return NULL;

    strncpy(d->base.name, name, sizeof(d->base.name) - 1);
    d->base.name[sizeof(d->base.name) - 1] = '\0';
    strcpy(d->secret, "dog-secret");

    return d;
}

void Dog_speak(Dog* d) {
    printf("%s says: woof!\n", d->base.name);
}

const char* Dog_getSecret(Dog* d) {
    return d->secret;
}


void dog_print(Dog* d) {
    printf("[Dog] %s (species=%s)\n", d->base.name, Dog_species);
}